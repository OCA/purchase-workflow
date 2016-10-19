# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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
#

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'order_id desc, sequence, id'

    sequence = fields.Integer(default=10,
                              help="Gives the sequence of this line when "
                                   "displaying the purchase order.")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self)._prepare_inv_line(
            account_id,
            order_line,
            )
        res['sequence'] = order_line.sequence
        return res

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order,
            order_line,
            picking_id,
            group_id)
        if res:
            res[0]['sequence'] = order_line.sequence
        return res

    @api.one
    @api.depends('order_line')
    def compute_max_line_sequence(self):
        """Allow to know the highest sequence
        entered in purchase order lines.
        Web add 10 to this value for the next sequence
        This value is given to the context of the o2m field
        in the view. So when we create new purchase order lines,
        the sequence is automatically max_sequence + 10
        """
        self.max_line_sequence = (
            max(self.mapped('order_line.sequence') or [0]) + 10)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='compute_max_line_sequence')


class PurchaseLineInvoice(models.TransientModel):
    _inherit = 'purchase.order.line_invoice'

    @api.multi
    def makeInvoices(self):
        invoice_line_obj = self.env['account.invoice.line']
        purchase_line_obj = self.env['purchase.order.line']
        ctx = self.env.context.copy()
        res = super(PurchaseLineInvoice, self.with_context(ctx)).makeInvoices()
        invoice_ids = []
        for field, op, val in safe_eval(res['domain']):
            if field == 'id':
                invoice_ids = val
                break

        invoice_lines = invoice_line_obj.search(
            [('invoice_id', 'in', invoice_ids)])
        for invoice_line in invoice_lines:
            order_line = purchase_line_obj.search(
                [('invoice_lines', '=', invoice_line.id)],
                limit=1
                )
            if not order_line:
                continue

            if not invoice_line.sequence:
                invoice_line.write({'sequence': order_line.sequence})

        return res
