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
from openerp import api, fields, models, _, exceptions
import openerp.addons.decimal_precision as dp


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"

    supplier_id = fields.Many2one('res.partner', string='Supplier',
                                  required=False,
                                  domain=[('supplier', '=', True)])
    item_ids = fields.One2many(
        'purchase.request.line.make.purchase.order.item',
        'wiz_id', string='Items')
    purchase_order_id = fields.Many2one('purchase.order',
                                        string='Purchase Order',
                                        required=False,
                                        domain=[('state', '=', 'draft')])

    @api.model
    def _default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_obj = self.env['res.company']
        company_id = company_obj._company_default_get('stock.warehouse')
        warehouses = warehouse_obj.search(
            [('company_id', '=', company_id)], limit=1)

        if warehouses:
            return warehouses[0]
        else:
            return False

    @api.model
    def _prepare_item(self, line):
        return {
            'line_id': line.id,
            'request_id': line.request_id.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'product_qty': line.product_qty,
            'product_uom_id': line.product_uom_id.id,
            'analytic_account_id': line.analytic_account_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).default_get(
            fields)
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not request_line_ids:
            return res
        assert active_model == 'purchase.request.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(request_line_ids):
                items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items
        return res

    @api.model
    def _prepare_purchase_order(self, warehouse_id, company_id):
        warehouse_obj = self.env['stock.warehouse']
        if not self.supplier_id:
            raise exceptions.Warning(
                _('Enter a supplier.'))
        warehouse = warehouse_obj.browse(warehouse_id)
        supplier = self.supplier_id
        location_id = warehouse.wh_input_stock_loc_id.id
        supplier_pricelist = supplier.property_product_pricelist_purchase  \
            or False
        data = {
            'origin': '',
            'partner_id': self.supplier_id.id,
            'pricelist_id': supplier_pricelist.id,
            'location_id': location_id,
            'fiscal_position': supplier.property_account_position and
            supplier.property_account_position.id or False,
            'warehouse_id': warehouse_id,
            'company_id': company_id,
            }
        return data

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        po_line_obj = self.env['purchase.order.line']
        product_uom = self.env['product.uom']
        product = item.product_id
        default_uom_po_id = product.uom_po_id.id
        qty = product_uom._compute_qty(item.product_uom_id.id,
                                       item.product_qty,
                                       default_uom_po_id)
        supplier_pricelist = \
            po.partner_id.property_product_pricelist_purchase \
            and po.partner_id.property_product_pricelist_purchase.id or False
        vals = po_line_obj.onchange_product_id(
            supplier_pricelist, product.id, qty, default_uom_po_id,
            po.partner_id.id, date_order=False,
            fiscal_position_id=po.partner_id.property_account_position.id,
            date_planned=item.line_id.date_required,
            name=False, price_unit=False, state='draft')['value']
        vals.update({
            'order_id': po.id,
            'product_id': product.id,
            'account_analytic_id': item.line_id.analytic_account_id.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
            'purchase_request_lines': [(4, item.line_id.id)],
            'date_planned':
                vals.get('date_planned', False) or item.line_id.date_required,
        })
        return vals

    @api.model
    def _get_order_line_search_domain(self, order, item):
        vals = self._prepare_purchase_order_line(order, item)
        order_line_data = [('order_id', '=', order.id),
                           ('product_id', '=', item.product_id.id or False),
                           ('product_uom', '=', vals['product_uom']),
                           ('account_analytic_id', '=',
                            item.line_id.analytic_account_id.id or False)]
        if not item.product_id:
            order_line_data.append(('name', '=', item.name))
        return order_line_data

    @api.multi
    def make_purchase_order(self):
        res = []
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        pr_line_obj = self.env['purchase.request.line']
        company_id = False
        warehouse_id = False
        purchase = False
        for item in self.item_ids:
            line = item.line_id
            if line.purchase_state == 'done':
                raise exceptions.Warning(
                    _('The purchase has already been completed.'))
            if item.product_qty <= 0.0:
                raise exceptions.Warning(
                    _('Enter a positive quantity.'))
            line_company_id = line.company_id \
                and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

            line_warehouse_id = line.request_id.warehouse_id \
                and line.request_id.warehouse_id.id or False
            if not line_warehouse_id:
                raise exceptions.Warning(
                    _('You have to enter a Warehouse.'))
            if warehouse_id is not False \
                    and line_warehouse_id != warehouse_id:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same Warehouse.'))
            else:
                warehouse_id = line_warehouse_id

            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(warehouse_id,
                                                       company_id)
                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            if available_po_lines:
                po_line = available_po_lines[0]
                new_qty, new_price = pr_line_obj._calc_new_qty_price(
                    line, po_line=po_line)
                if new_qty > po_line.product_qty:
                        po_line.product_qty = new_qty
                        po_line.price_unit = new_price
                        po_line.purchase_request_lines = [(4, line.id)]
            else:
                po_line_data = self._prepare_purchase_order_line(purchase,
                                                                 item)
                po_line_obj.create(po_line_data)
            res.append(purchase.id)

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


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order.item"
    _description = "Purchase Request Line Make Purchase Order Item"

    wiz_id = fields.Many2one(
        'purchase.request.line.make.purchase.order',
        string='Wizard', required=True, ondelete='cascade',
        readonly=True)
    line_id = fields.Many2one('purchase.request.line',
                              string='Purchase Request Line',
                              required=True,
                              readonly=True)
    request_id = fields.Many2one('purchase.request',
                                 related='line_id.request_id',
                                 string='Purchase Request',
                                 readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', required=True)
    product_qty = fields.Float(string='Quantity to purchase',
                               digits_compute=dp.get_precision('Product UoS'))
    product_uom_id = fields.Many2one('product.uom', string='UoM')

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
