# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tools.translate import _
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class PurchaseRequestLineMakePurchaseOrder(orm.TransientModel):
    _name = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"

    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier',
                                       required=False,
                                       domain=[('supplier', '=', True)]),
        'item_ids': fields.one2many(
            'purchase.request.line.make.purchase.order.item',
            'wiz_id', 'Items'),
        'purchase_order_id': fields.many2one('purchase.order',
                                             'Purchase Order',
                                             required=False,
                                             domain=[('state', '=', 'draft')]),
    }

    def _default_warehouse(self, cr, uid, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
                                                      'stock.warehouse',
                                                      context=context)
        if context is None:
            context = {}

        warehouse_ids = warehouse_obj.search(
            cr, uid, [('company_id', '=', company_id)], limit=1,
            context=context) or []

        if warehouse_ids:
            return warehouse_ids[0]
        else:
            return False

    def _prepare_item(self, cr, uid, line, context=None):
        return [{
            'line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'product_qty': line.product_qty,
            'product_uom_id': line.product_uom_id.id,
            'account_analytic_id': line.analytic_account_id.id,
        }]

    def default_get(self, cr, uid, fields, context=None):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).default_get(
            cr, uid, fields, context=context)
        request_line_obj = self.pool['purchase.request.line']
        request_line_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not request_line_ids:
            return res
        assert active_model == 'purchase.request.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(cr, uid, request_line_ids,
                                            context=context):
                items += self._prepare_item(cr, uid, line, context=context)
        res['item_ids'] = items

        return res

    def _prepare_purchase_order(self, cr, uid, make_purchase_order,
                                warehouse_id, company_id,
                                context=None):
        warehouse_obj = self.pool['stock.warehouse']
        if not make_purchase_order.supplier_id:
                raise orm.except_orm(
                    _('Could not create purchase order !'),
                    _('Enter a supplier.'))
        warehouse = warehouse_obj.browse(cr, uid, warehouse_id,
                                         context=context)
        supplier = make_purchase_order.supplier_id
        location_id = warehouse.lot_input_id.id
        supplier_pricelist = supplier.property_product_pricelist_purchase \
            or False
        data = {
            'origin': '',
            'partner_id': make_purchase_order.supplier_id.id,
            'pricelist_id': supplier_pricelist.id,
            'location_id': location_id,
            'fiscal_position': supplier.property_account_position and
            supplier.property_account_position.id or False,
            'warehouse_id': warehouse_id,
            'company_id': company_id,
            }
        return data

    def _prepare_purchase_order_line(self, cr, uid, po_id,
                                     make_purchase_order, item,
                                     context=None):
        fiscal_position = self.pool['account.fiscal.position']
        purchase_req_line_obj = self.pool['purchase.request.line']
        po_obj = self.pool['purchase.order']
        if po_id:
            po = po_obj.browse(cr, uid, po_id, context=context)
            supplier = po.partner_id
        else:
            supplier = make_purchase_order.supplier_id
        product = item.product_id
        seller_price, qty, default_uom_po_id, date_planned = \
            purchase_req_line_obj._seller_details(cr, uid, item.line_id,
                                                  supplier, context=context)
        taxes_ids = product.supplier_taxes_id
        taxes = fiscal_position.map_tax(
            cr, uid, supplier.property_account_position, taxes_ids)

        analytic_id = item.line_id.analytic_account_id and \
            item.line_id.analytic_account_id.id or False
        return {
            'order_id': po_id,
            'name': product.partner_ref,
            'product_qty': qty,
            'product_id': product.id,
            'product_uom': default_uom_po_id,
            'price_unit': seller_price,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes)],
            'account_analytic_id': analytic_id,
            'purchase_request_lines': [(4, item.line_id.id)]
        }

    def _get_order_line_search_domain(self, cr, uid, order_id, request_line,
                                      context=None):
        return [('requisition_id', '=', order_id),
                ('product_id', '=', request_line.product_id.id),
                ('product_uom_id', '=', request_line.product_uom_id.id)]

    def make_purchase_order(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        make_purchase_order = self.browse(cr, uid, ids[0], context=context)
        purchase_obj = self.pool['purchase.order']
        po_line_obj = self.pool['purchase.order.line']
        pr_line_obj = self.pool['purchase.request.line']
        company_id = False
        warehouse_id = False
        purchase_id = False
        for item in make_purchase_order.item_ids:
            line = item.line_id
            if line.purchase_state == 'done':
                raise orm.except_orm(
                    _('Could not process !'),
                    _('The purchase has already been completed.'))
            if item.product_qty <= 0.0:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('Enter a positive quantity.'))
            line_company_id = line.company_id \
                and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

            line_warehouse_id = line.request_id.warehouse_id \
                and line.request_id.warehouse_id.id or False
            if not line_warehouse_id:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('You have to enter a Warehouse.'))
            if warehouse_id is not False \
                    and line_warehouse_id != warehouse_id:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('You have to select lines '
                      'from the same Warehouse.'))
            else:
                warehouse_id = line_warehouse_id

            if make_purchase_order.purchase_order_id:
                purchase_id = make_purchase_order.purchase_order_id.id
            if not purchase_id:
                po_data = self._prepare_purchase_order(cr, uid,
                                                       make_purchase_order,
                                                       warehouse_id,
                                                       company_id,
                                                       context=context)
                purchase_id = purchase_obj.create(cr, uid, po_data,
                                                  context=context)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(
                cr, uid, purchase_id, line, context=context)
            available_po_line_ids = po_line_obj.search(
                cr, uid, domain, context=context)
            if available_po_line_ids:
                po_line = po_line_obj.browse(
                    cr, uid, available_po_line_ids[0], context=context)
                new_qty, new_price = pr_line_obj._calc_new_qty_price(
                        cr, uid, line, po_line=po_line,
                        context=context)
                if new_qty > po_line.product_qty:
                        po_line_obj.write(
                            cr, uid, po_line.id,
                            {'product_qty': new_qty,
                             'price_unit': new_price},
                            context=context)
            else:
                po_line_data = self._prepare_purchase_order_line(
                    cr, uid, purchase_id, make_purchase_order,
                    item, context=context)
                po_line_obj.create(cr, uid, po_line_data, context=context)
            res.append(purchase_id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Purchase order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseOrderItem(orm.TransientModel):
    _name = "purchase.request.line.make.purchase.order.item"
    _description = "Purchase Request Line Make Purchase Order Item"

    _columns = {
        'wiz_id': fields.many2one(
            'purchase.request.line.make.purchase.order',
            'Wizard', required=True, ondelete='cascade',
            readonly=True),
        'line_id': fields.many2one('purchase.request.line',
                                   'Purchase Request Line',
                                   required=True,
                                   readonly=True),
        'product_id': fields.related('line_id',
                                     'product_id', type='many2one',
                                     relation='product.product',
                                     string='Product',
                                     readonly=True),
        'product_qty': fields.float(string='Quantity to deliver',
                                    digits_compute=dp.get_precision(
                                        'Product UoS')),
        'product_uom_id': fields.related('line_id',
                                         'product_uom_id', type='many2one',
                                         relation='product.uom',
                                         string='UoM',
                                         readonly=True),
        'name': fields.related('line_id',
                               'name', type='char',
                               string='Description',
                               readonly=True)

    }
