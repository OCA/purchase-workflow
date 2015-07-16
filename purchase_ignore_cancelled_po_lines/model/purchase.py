# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
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
from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class PurchaseOrder(orm.Model):

    _inherit = 'purchase.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                if line.state == 'cancel':
                    continue
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(
                        cr, uid, line.taxes_id, line.price_unit,
                        line.product_qty, line.product_id,
                        order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = \
                res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(
                cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax",
            track_visibility='always'),
        'amount_tax': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(
            _amount_all, digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),

    }

    def _minimum_planned_date(self, cr, uid, ids, field_name, arg,
                              context=None):
        res = super(PurchaseOrder, self)._minimum_planned_date(
            cr, uid, ids, field_name, arg, context=context)
        purchase_obj = self.browse(cr, uid, ids, context=context)
        for purchase in purchase_obj:
            res[purchase.id] = False
            if purchase.order_line:
                min_date = purchase.order_line[0].date_planned
                for line in purchase.order_line:
                    if line.state == 'cancel':
                        continue
                    if line.date_planned < min_date:
                        min_date = line.date_planned
                res[purchase.id] = min_date
        return res

    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = super(PurchaseOrder, self)._invoiced(
            cursor, user, ids, name, arg, context=context)
        for purchase in self.browse(cursor, user, ids, context=context):
            res[purchase.id] = \
                all(line.invoiced for line in purchase.order_line
                    if line.state != 'cancel')
        return res

    def set_order_line_status(self, cr, uid, ids, status, context=None):
        # We restrict the usage of the method to be used only if you want to
        #  cancel a sales order line.
        if status != 'cancel':
                raise orm.except_orm(
                    _('Error!'), _("It is not possible to set the order line "
                                   "status to a value different than "
                                   "Cancelled."))
        return super(PurchaseOrder, self).set_order_line_status(
            cr, uid, ids, status, context=context)

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.invoice_method == 'picking' \
                    and not any([l.product_id
                                 and l.product_id.type in ('product', 'consu')
                                 and l.state != 'cancel'
                                 for l in po.order_line]):
                raise orm.except_orm(
                    _('Error!'), _("You cannot confirm a purchase order with "
                                   "Invoice Control Method 'Based on incoming "
                                   "shipments' that doesn't contain any "
                                   "stockable item."))
        return super(PurchaseOrder, self).wkf_confirm_order(
            cr, uid, ids, context=context)

    def action_invoice_create(self, cr, uid, ids, context=None):
        inv_line_obj = self.pool['account.invoice.line']
        res = super(PurchaseOrder, self).action_invoice_create(
            cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids, context=context):
            for po_line in order.order_line:
                if po_line.state == 'cancel':
                    # Remove the corresponding invoice line
                    for inv_line in po_line.invoice_lines:
                        inv_line_obj.unlink(cr, uid, [inv_line.id],
                                            context=context)
        return res

    def has_stockable_product(self, cr, uid, ids, *args):
        res = super(PurchaseOrder, self).has_stockable_product(
            cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.state == 'cancel':
                    return False
        return res

    def _create_pickings(self, cr, uid, order, order_lines,
                         picking_id=False, context=None):
        for order_line in order_lines:
            if not order_line.product_id:
                return [picking_id]
        return super(PurchaseOrder, self)._create_pickings(
            cr, uid, order, order_lines, picking_id=False, context=context)

    def do_merge(self, cr, uid, ids, context=None):
        # As we do not want to override the default merge action, because we
        #  would not be able to call super, at least we will not allow
        # merging PO's containing cancelled lines.
        for porder in [order for order in self.browse(cr, uid, ids,
                                                      context=context)
                       if order.state == 'draft']:
            for order_line in porder.order_line:
                if order_line.state == 'cancel':
                    raise orm.except_orm(
                        _('Error!'), _("You cannot merge purchase orders "
                                       "that contain cancelled items."))
        return super(PurchaseOrder, self).do_merge(
            cr, uid, ids, context=context)
