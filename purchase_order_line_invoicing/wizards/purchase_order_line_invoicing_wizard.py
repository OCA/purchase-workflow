# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderLineInvoiceWizard(models.TransientModel):
    _name = 'purchase.order.line.invoice.wizard'

    purchase_order_line_details_ids = fields.One2many(
        comodel_name='purchase.order.line.invoice.details',
        inverse_name='wizard_id')

    @api.model
    def _check_unique_partner(self, lines):
        partner = lines.mapped('partner_id')
        if len(partner) != 1:
            raise UserError(_(
                """You have to select line from only one supplier."""))

    def _prepare_default_line_vals(self, purchase_line):
        return {
            'purchase_order_line_id': purchase_line.id,
            'order_id': purchase_line.order_id.id,
            'product_id': purchase_line.product_id.id,
            'name': purchase_line.name,
            'price_unit': purchase_line.price_unit,
            'product_qty': purchase_line.product_qty,
            'price_subtotal': purchase_line.price_subtotal,
            'qty_received': purchase_line.qty_received,
            'qty_invoiced': purchase_line.qty_invoiced,
            'invoice_qty': max(
                purchase_line.qty_received - purchase_line.qty_invoiced, 0),
        }

    @api.model
    def default_get(self, fields):
        result = super(PurchaseOrderLineInvoiceWizard,
                       self).default_get(fields)

        if self.env.context.get('active_domain', False):
            domain = self.env.context.get('active_domain', False)
        else:
            domain = [('id', 'in', self.env.context.get('active_ids', []))]
        purchase_lines = self.env['purchase.order.line'].search(domain)

        if not purchase_lines:
            raise UserError(_('Please select a least one line to invoice.'))
        details = []
        self._check_unique_partner(purchase_lines)
        for line in purchase_lines:
            vals = self._prepare_default_line_vals(line)
            details.append(
                (0, 0, vals))

        if details:
            result['purchase_order_line_details_ids'] = details
        return result

    def create_invoice(self):
        self.ensure_one()
        invoice_lines_data = []
        purchase_order = self.env['purchase.order']
        for line in self.purchase_order_line_details_ids:
            line_data = self.env[
                'account.invoice']._prepare_invoice_line_from_po_line(
                line.purchase_order_line_id)
            line_data['invoice_line_tax_ids'] = [
                (6, 0, line_data['invoice_line_tax_ids'])]
            line_data['quantity'] = line.invoice_qty
            invoice_lines_data.append((0, 0, line_data))
            if line.purchase_order_line_id.order_id not in purchase_order:
                purchase_order += line.purchase_order_line_id.order_id

        default_journal_id = self.env['account.invoice'].\
            with_context(type='in_invoice')._default_journal()

        invoice_data = {
            'partner_id': purchase_order[0].partner_id.id,
            'type': 'in_invoice',
            'origin': ','.join(purchase_order.mapped('name')),
            'invoice_line_ids': invoice_lines_data
        }
        if default_journal_id:
            invoice_data['journal_id'] = default_journal_id.id
        invoice = self.env['account.invoice'].create(invoice_data)

        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        res = self.env.ref('account.invoice_supplier_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = invoice.id

        return result


class PurchaseOrderLineInvoiceDetails(models.TransientModel):
    _name = 'purchase.order.line.invoice.details'

    wizard_id = fields.Many2one(
        comodel_name='purchase.order.line.invoice.wizard',
        required=True,
        ondelete='cascade')
    purchase_order_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        ondelete='cascade',
        required=True)
    order_id = fields.Many2one(
        related='purchase_order_line_id.order_id',
        readonly=True)
    product_id = fields.Many2one(
        related='purchase_order_line_id.product_id',
        readonly=True)
    name = fields.Text(
        related='purchase_order_line_id.name',
        readonly=True)
    product_qty = fields.Float(
        related='purchase_order_line_id.product_qty',
        readonly=True)
    price_unit = fields.Float(
        related='purchase_order_line_id.price_unit',
        readonly=True)
    price_subtotal = fields.Monetary(
        related='purchase_order_line_id.price_subtotal',
        readonly=True)
    currency_id = fields.Many2one(
        related='purchase_order_line_id.currency_id',
        readonly=True)
    qty_invoiced = fields.Float(
        related='purchase_order_line_id.qty_invoiced',
        readonly=True)
    qty_received = fields.Float(
        related='purchase_order_line_id.qty_received',
        readonly=True)
    invoice_qty = fields.Float(
        'Quantity to Invoice',
        required=True)
