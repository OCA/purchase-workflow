# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from openerp.tools import float_is_zero, float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.qty_received')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        super(PurchaseOrder, self)._get_invoiced()
        for order in self:
            for line in order.order_line:
                if line.state == 'purchase' and \
                        line.product_id.purchase_method == 'receive':
                    if not float_is_zero(line.qty_to_invoice,
                                         precision_digits=precision):
                        break
                    elif float_compare(line.qty_invoiced, line.qty_received,
                                       precision_digits=precision) == -1:
                        order.invoice_status = 'to invoice'
                        break
                    elif float_compare(line.qty_invoiced, line.qty_received,
                                       precision_digits=precision) >= 0:
                        order.invoice_status = 'invoiced'
                        break

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoiced(self):
        """
        Attention! This method overrides the standard method of Odoo.

        Compute the invoice status of a PO. Possible statuses:
        - no: if the PO is not in status 'purchase' or 'done', we consider that
        there is nothing to be billed for. This is also the default value if
        the conditions of no other status is met.
        - to invoice: if any PO line is 'to invoice', the whole PO is 'to
        invoice'
        - invoiced: if all PO lines are invoiced, the PO is invoiced.

        The invoice_ids are obtained thanks to the invoice lines of the PO
        lines, and we also search for possible refunds created directly from
        existing invoices. This is necessary since such a
        refund is not directly linked to the PO.
        """
        for order in self:
            line_invoice_status = [line.invoice_status for line in
                                   order.order_line]

            if order.state not in ('purchase', 'done'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice'
                     for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced'
                     for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            else:
                invoice_status = 'no'

            order.invoice_status = invoice_status


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.type')
    def _compute_qty_invoiced(self):
        """
        Attention! This method overrides the standard method of Odoo.

        """
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    inv_qty = inv_line.uom_id._compute_qty_obj(
                        inv_line.uom_id, inv_line.quantity, line.product_uom)
                    if inv_line.invoice_id.type == 'in_invoice':
                        qty += inv_qty
                    else:
                        qty -= inv_qty
            line.qty_invoiced = qty

    @api.depends('product_qty', 'qty_received', 'qty_to_invoice',
                 'qty_invoiced', 'order_id.state')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a PO line. Possible statuses:
        - no: if the PO is not in status 'purchase' or 'done', we consider that
        there is nothing to be billed for. This is also the default value if
        the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line.
        Refer to method `_compute_qty_to_invoice()` for more information on
        how this quantity is calculated.
        - invoiced: the quantity invoiced is larger or equal to the quantity
        ordered.
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            if line.state not in ('purchase', 'done'):
                line.invoice_status = 'no'
            elif line.state == 'done':
                if float_is_zero(line.qty_invoiced,
                                 precision_digits=precision):
                    line.invoice_status = 'no'
                else:
                    line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice,
                                   precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif float_compare(line.qty_invoiced, line.product_qty,
                               precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    @api.depends('qty_invoiced', 'qty_received', 'product_qty',
                 'order_id.state')
    def _compute_qty_to_invoice(self):
        """
        Compute the quantity to be billed. If the Control Purchase Bills is
        in ordered quantities, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity
        received is used.
        """
        for line in self:
            if line.order_id.state == 'purchase':
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - \
                        line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    invoice_status = fields.Selection([
        ('no', 'Not purchased'),
        ('to invoice', 'Waiting Invoices'),
        ('invoiced', 'Invoice Received'),
        ], string='Invoice Status', compute='_compute_invoice_status',
        store=True, readonly=True, copy=False, default='no')

    qty_to_invoice = fields.Float(compute='_compute_qty_to_invoice',
                                  string="To Be Billed Qty", store=True)
