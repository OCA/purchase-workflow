from odoo import _, api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    expense_ids = fields.One2many(
        compute="_compute_expense_ids",
        comodel_name="hr.expense",
        string="Related Expenses",
    )

    expense_count = fields.Integer(
        string="Expense Count",
        compute="_compute_expense_ids",
    )

    def _get_related_expenses(self):
        self.ensure_one()
        return self.env["hr.expense"].search(
            [("purchase_request_line_id", "in", self.line_ids.ids)]
        )

    @api.depends("line_ids.expense_ids")
    def _compute_expense_ids(self):
        for request in self:
            expenses = request.line_ids.mapped("expense_ids")
            request.update({
                "expense_ids": expenses,
                "expense_count": len(expenses)
            })

    def action_view_expenses(self):
        self.ensure_one()
        expenses = self._get_related_expenses()
        action = {
            "name": _("Expenses"),
            "type": "ir.actions.act_window",
            "res_model": "hr.expense",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.expense_ids.ids)],
            "context": {"create": False},
        }
        if len(expenses) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": expenses.id,
                }
            )
        return action
