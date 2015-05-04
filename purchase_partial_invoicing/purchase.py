# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class purchase_order_line(orm.Model):

    def _invoiced_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            invoiced_qty = 0.0
            for invoice_line in line.invoice_lines:
                invoiced_qty += invoice_line.quantity
            res[line.id] = invoiced_qty
        return res

    def _fully_invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = line.invoiced_qty == line.product_qty
        return res

    def _all_invoices_approved(self, cursor, user, ids, name, arg,
                               context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if line.invoice_lines:
                res[line.id] = not any(inv_line.invoice_id.state
                                       in ['draft', 'cancel']
                                       for inv_line in line.invoice_lines)
            else:
                res[line.id] = False
        return res

    def _order_lines_from_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for invoice in self.pool['account.invoice'].browse(cr, uid, ids,
                                                           context=context):
            for line in invoice.invoice_line:
                result[line.purchase_line_id.id] = True
        return result.keys()

    _inherit = 'purchase.order.line'

    _columns = {
        'invoiced_qty': fields.function(
            _invoiced_qty,
            string='Invoiced quantity',
            type='float',
            copy=False,
            store={
                   'account.invoice': (_order_lines_from_invoice_line, [], 5),
                   'purchase.order.line': (lambda self, cr, uid, ids,
                                           context=None: ids,
                                           ['invoice_lines'], 5)}),
        'fully_invoiced': fields.function(
            _fully_invoiced,
            string='Fully invoiced',
            type='boolean',
            copy=False,
            store={
                   'account.invoice': (_order_lines_from_invoice_line, [], 10),
                   'purchase.order.line': (lambda self, cr, uid, ids,
                                           context=None: ids,
                                           ['invoice_lines'], 10)}),
        'all_invoices_approved': fields.function(
            _all_invoices_approved,
            string='All invoices approved',
            type='boolean'),
    }


class purchase_order(orm.Model):

    _inherit = 'purchase.order'

    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for purchase in self.browse(cursor, user, ids, context=context):
            res[purchase.id] = all(line.all_invoices_approved and
                                   line.fully_invoiced
                                   for line in purchase.order_line)
        return res

    _columns = {
        'invoiced': fields.function(_invoiced, string='Invoice Received',
                                    type='boolean',
                                    help="It indicates that an invoice has "
                                         "been validated"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        if context is None:
            context = {}
        res = super(purchase_order, self).\
            _prepare_inv_line(cr, uid, account_id, order_line, context=context)
        if context.get('partial_quantity_lines'):
            partial_quantity_lines = context.get('partial_quantity_lines')
            if partial_quantity_lines.get(order_line.id):
                res.update({'quantity':
                            partial_quantity_lines.get(order_line.id)})
        return res


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids,
                                                            context=context)
        purchase_order_obj = self.pool.get('purchase.order')
        po_ids = purchase_order_obj.search(
            cr, uid, [('invoice_ids', 'in', ids)], context=context)
        for purchase_order in purchase_order_obj.browse(cr, uid, po_ids,
                                                        context=context):
            for po_line in purchase_order.order_line:
                if po_line.invoiced_qty != po_line.product_qty:
                    po_line.write({'invoiced': False})
        return res
