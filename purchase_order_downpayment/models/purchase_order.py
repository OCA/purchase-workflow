from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_payment_ids = fields.One2many(
        "account.payment",
        "purchase_id",
        string="Purchase Payment",
    )

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.account_payment_ids)

    payment_count = fields.Integer(compute="_compute_payment_count")

    def action_open_payment(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments_payable"
        )
        action.update({"domain": [("purchase_id", "=", self.id)]})
        return action
