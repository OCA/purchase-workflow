# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import fields, models


class ImportInvoiceLine(models.TransientModel):
    _name = "import.invoice.line.wizard"
    _description = "Import supplier invoice line"

    supplier = fields.Many2one(
        comodel_name="res.partner", string="Supplier", required=True,
    )
    invoice = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=True,
        domain="[('partner_id', '=', supplier), ('type', '=', 'in_invoice'),"
        "('state', '=', 'posted')]",
    )
    invoice_line = fields.Many2one(
        comodel_name="account.move.line",
        string="Invoice line",
        required=True,
        domain="[('move_id', '=', invoice)]",
    )
    expense_type = fields.Many2one(
        comodel_name="purchase.expense.type", string="Expense type", required=True
    )

    def action_import_invoice_line(self):
        self.ensure_one()
        dist_id = self.env.context["active_id"]
        distribution = self.env["purchase.cost.distribution"].browse(dist_id)
        currency_from = self.invoice_line.currency_id
        amount = self.invoice_line.price_subtotal
        currency_to = distribution.currency_id
        company = distribution.company_id or self.env.user.company_id
        cost_date = distribution.date or fields.Date.today()
        expense_amount = currency_from._convert(amount, currency_to, company, cost_date)
        self.env["purchase.cost.distribution.expense"].create(
            {
                "distribution": dist_id,
                "invoice_line": self.invoice_line.id,
                "invoice_id": self.invoice_line.move_id.id,
                "ref": self.invoice_line.name,
                "expense_amount": expense_amount,
                "type": self.expense_type.id,
            }
        )
