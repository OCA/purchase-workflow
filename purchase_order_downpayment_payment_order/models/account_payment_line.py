from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    purchase_id = fields.Many2one(
        "purchase.order",
        "Purchase",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _prepare_account_payment_vals(self):
        """add purchase_id of the payment line to the account payment."""
        vals = super()._prepare_account_payment_vals()
        vals["purchase_id"] = self.purchase_id.id
        return vals
