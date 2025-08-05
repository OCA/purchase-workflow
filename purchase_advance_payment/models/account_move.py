# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        # Automatic reconciliation of payment when bill confirmed.
        res = super().action_post()
        for move in self:
            # Link advance payments without move_id to the new bill.
            purchase_order = move.line_ids.purchase_order_id
            move.matched_payment_ids = purchase_order.account_payment_ids.filtered(
                lambda p: not p.outstanding_account_id
                and not p.move_id
                and not p.invoice_ids
            )
        if bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
        ):
            for move in self:
                purchase_order = move.line_ids.purchase_order_id
                if (
                    purchase_order
                    and move.invoice_outstanding_credits_debits_widget is not False
                ):
                    json_invoice_outstanding_data = (
                        move.invoice_outstanding_credits_debits_widget.get(
                            "content", []
                        )
                    )
                    for data in json_invoice_outstanding_data:
                        if (
                            data.get("move_id")
                            in purchase_order.account_payment_ids.move_id.ids
                        ):
                            move.js_assign_outstanding_line(line_id=data.get("id"))
        return res
