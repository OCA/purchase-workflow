# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.make.planned.invoice"

    def create_invoices_by_plan(self):
        # Create advance, if any
        purchase = self.env["purchase.order"].browse(self.env.context.get("active_id"))
        purchase.ensure_one()
        plan_advance = purchase.invoice_plan_ids.filtered(
            lambda pln: pln.to_invoice and pln.invoice_type == "advance"
        )
        if plan_advance:  # Create advance invoice using percentage
            MakeInvoice = self.env["purchase.advance.payment.inv"]
            makeinv_wizard = {
                "advance_payment_method": "percentage",
                "amount": plan_advance.percent,
            }
            makeinvoice = MakeInvoice.create(makeinv_wizard)
            makeinvoice.with_context(invoice_plan_id=plan_advance.id).create_invoices()
        # If PO has deposit and deduct option not yet chosen,
        # show the Advance/Deposit Deduction Option wizard
        # (reuses purchase_deposit's wizard to maintain consistent UX)
        if not self.env.context.get("advance_deduct_option"):
            has_deposit = bool(purchase.order_line.filtered("is_deposit"))
            if has_deposit:
                wizard_view = self.env.ref(
                    "purchase_deposit.view_purchase_advance_deduct_option"
                )
                return {
                    "name": self.env._("Advance/Deposit Deduction Option"),
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": "purchase.advance.deduct.option",
                    "views": [(wizard_view.id, "form")],
                    "view_id": wizard_view.id,
                    "target": "new",
                    "context": dict(self.env.context),
                }

        # Create non-advance invoices
        if self.env.context.get("all_remain_invoices") or not plan_advance:
            return super().create_invoices_by_plan()
        return {"type": "ir.actions.act_window_close"}
