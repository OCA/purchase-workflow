# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import api, fields, models


class ImportInvoiceLine(models.TransientModel):
    _name = "import.invoice.line.wizard"
    _description = "Import supplier invoice line"

    supplier = fields.Many2one(
        comodel_name='res.partner', string='Supplier', required=True,
        domain="[('supplier',  '=', True)]")
    invoice = fields.Many2one(
        comodel_name='account.invoice', string="Invoice", required=True,
        domain="[('partner_id', '=', supplier), ('type', '=', 'in_invoice'),"
               "('state', 'in', ['open', 'paid'])]")
    invoice_line = fields.Many2one(
        comodel_name='account.invoice.line', string="Invoice line",
        required=True, domain="[('invoice_id', '=', invoice)]")
    expense_type = fields.Many2one(
        comodel_name='purchase.expense.type', string='Expense type',
        required=True)

    @api.multi
    def action_import_invoice_line(self):
        self.ensure_one()
        self.env['purchase.cost.distribution.expense'].create({
            'distribution': self.env.context['active_id'],
            'invoice_line': self.invoice_line.id,
            'invoice_id': self.invoice_line.invoice_id.id,
            'ref': self.invoice_line.name,
            'expense_amount': self.invoice_line.price_subtotal,
            'type': self.expense_type.id,
        })
