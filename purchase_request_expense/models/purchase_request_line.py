from odoo import _, api, fields, models
from odoo import ValidationError


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    expense_ids = fields.One2many(
        comodel_name="hr.expense",
        inverse_name="purchase_request_line_id",
        string="Expenses",
        readonly=True,
    )

    expense_amount = fields.Monetary(
        string="Expense Amount",
        compute="_compute_expense_amount",
    )

    @api.depends("expense_ids", "expense_ids.total_amount")
    def _compute_expense_amount(self):
        for line in self:
            line.expense_amount = sum(line.expense_ids.mapped("total_amount"))

    @api.constrains("company_id", "request_id")
    def _check_company_consistency(self):
        for line in self:
            if (
                line.company_id
                and line.request_id.company_id
                and line.company_id != line.request_id.company_id
            ):
                raise ValidationError(
                    _("The company of the request line must match the company of the request.")
                )