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


class PurchaseRequestLineMakePurchaseRequisition(orm.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition"
    _description = "Purchase Request Line Make Purchase Requisition"

    _columns = {
        'item_ids': fields.one2many(
            'purchase.request.line.make.purchase.requisition.item',
            'wiz_id', 'Items'),
        'purchase_requisition_id': fields.many2one(
            'purchase.requisition', 'Purchase Requisition',
            required=False, domain=[('state', '=', 'draft')]),
    }

    def _prepare_item(self, cr, uid, line, context=None):
        return [{
            'line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'product_qty': line.product_qty,
            'product_uom_id': line.product_uom_id.id,
        }]

    def default_get(self, cr, uid, fields, context=None):
        res = super(PurchaseRequestLineMakePurchaseRequisition,
                    self).default_get(cr, uid, fields, context=context)
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

    def _prepare_purchase_requisition(self, cr, uid,
                                      make_purchase_requisition,
                                      warehouse_id,
                                      company_id,
                                      context=None):
        data = {
            'origin': '',
            'warehouse_id': warehouse_id,
            'company_id': company_id,
            }
        return data

    def _prepare_purchase_requisition_line(self, cr, uid, pr_id,
                                           make_purchase_order, item,
                                           context=None):
        return {
            'requisition_id': pr_id,
            'product_qty': item.product_qty,
            'product_id': item.line_id.product_id.id,
            'product_uom_id': item.line_id.product_uom_id.id,
            'purchase_request_lines': [(4, item.line_id.id)]
        }

    def _get_requisition_line_search_domain(self, cr, uid, requisition_id,
                                            request_line, context=None):
        return [('requisition_id', '=', requisition_id),
                ('product_id', '=', request_line.product_id.id),
                ('product_uom_id', '=', request_line.product_uom_id.id)]

    def make_purchase_requisition(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        make_purchase_requisition = self.browse(cr, uid, ids[0],
                                                context=context)
        pr_obj = self.pool['purchase.requisition']
        pr_line_obj = self.pool['purchase.requisition.line']
        company_id = False
        warehouse_id = False
        requisition_id = False
        for item in make_purchase_requisition.item_ids:
            line = item.line_id
            if line.state == 'done':
                raise orm.except_orm(
                    _('Could not process !'),
                    _('A related requisition has already been completed'))
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
            if warehouse_id is not False \
                    and line_warehouse_id != warehouse_id:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('You have to select lines '
                      'from the same warehouse.'))
            else:
                warehouse_id = line_warehouse_id

            if make_purchase_requisition.purchase_requisition_id:
                requisition_id = \
                    make_purchase_requisition.purchase_requisition_id.id
            if not requisition_id:
                preq_data = self._prepare_purchase_requisition(
                    cr, uid, make_purchase_requisition, warehouse_id,
                    company_id, context=context)
                requisition_id = pr_obj.create(cr, uid, preq_data,
                                               context=context)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_requisition_line_search_domain(
                cr, uid, requisition_id, line, context=context)
            available_pr_line_ids = pr_line_obj.search(
                cr, uid, domain, context=context)
            if available_pr_line_ids:
                pr_line = pr_line_obj.browse(
                    cr, uid, available_pr_line_ids[0], context=context)
                new_qty = pr_line.product_qty + item.product_qty
                pr_line_obj.write(cr, uid, [pr_line.id], {
                    'product_qty': new_qty,
                    'purchase_request_lines': [(4, line.id)]},
                    context=context)
            else:
                po_line_data = self._prepare_purchase_requisition_line(
                    cr, uid, requisition_id, make_purchase_requisition,
                    item, context=context)
                pr_line_obj.create(cr, uid, po_line_data, context=context)
            res.append(requisition_id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Purchase requisition'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseRequisitionItem(orm.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition.item"
    _description = "Purchase Request Line Make Purchase Requisition Item"

    _columns = {
        'wiz_id': fields.many2one(
            'purchase.request.line.make.purchase.requisition',
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
