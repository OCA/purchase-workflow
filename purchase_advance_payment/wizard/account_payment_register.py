from odoo import Command, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        """Inherited method to relate payments automatically when generate payments from an account.move"""
        payments = super()._create_payments()
        ctx = self._context
        if ctx.get("active_model") == "account.move" and len(ctx.get("active_ids", [])) <= 1:
            move = self.env["account.move"].browse(ctx.get("active_id", [])).exists()
            orders = self.env["purchase.order"].search([("invoice_ids", "in", move.ids)])
            orders.write({"account_payment_ids": [Command.link(id) for id in payments.ids]})
        return payments
