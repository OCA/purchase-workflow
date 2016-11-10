# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):

    @api.one
    @api.depends('invoice_lines', 'invoice_lines.invoice_id',
                 'invoice_lines.quantity')
    def _compute_invoiced_qty(self):
        self.invoiced_qty = sum(self.invoice_lines.mapped('quantity'))

    @api.one
    @api.depends('invoice_lines', 'invoice_lines.invoice_id',
                 'invoice_lines.quantity', 'cancelled_qty')
    def _compute_fully_invoiced(self):
        self.fully_invoiced = \
            (self.invoiced_qty + self.cancelled_qty >= self.product_qty)

    @api.one
    def _compute_all_invoices_approved(self):
        if self.invoice_lines:
            self.all_invoices_approved = \
                not any(inv_line.invoice_id.state in ['draft', 'cancel']
                        for inv_line in self.invoice_lines)
        else:
            self.all_invoices_approved = False

    _inherit = 'purchase.order.line'

    invoiced_qty = fields.Float(
        compute='_compute_invoiced_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        copy=False, store=True)

    cancelled_qty = fields.Float(
        string='Cancelled Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        copy=False)

    fully_invoiced = fields.Boolean(
        compute='_compute_fully_invoiced', copy=False, store=True)

    all_invoices_approved = fields.Boolean(
        compute='_compute_all_invoices_approved')


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.one
    def _compute_invoiced(self):
        self.invoiced = all((line.all_invoices_approved or
                             line.product_qty == line.cancelled_qty) and
                            line.fully_invoiced
                            for line in self.order_line)

    invoiced = fields.Boolean(compute='_compute_invoiced')

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self).\
            _prepare_inv_line(account_id, order_line)
        ctx = self.env.context.copy()
        if ctx.get('partial_quantity_lines'):
            partial_quantity_lines = ctx.get('partial_quantity_lines')
            if order_line.id in partial_quantity_lines:
                res.update({'quantity':
                            partial_quantity_lines.get(order_line.id)})
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        purchase_order_obj = self.env['purchase.order']
        po_ids = purchase_order_obj.suspend_security()\
            .search([('invoice_ids', 'in', self.ids)])
        for purchase_order in po_ids:
            for po_line in purchase_order.order_line:
                total_quantity = po_line.invoiced_qty + po_line.cancelled_qty
                if total_quantity < po_line.product_qty:
                    po_line.invoiced = False
        return res
