# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.make.planned.invoice"

    def create_invoices_by_plan(self):
        # Create advance, if any
        purchase = self.env["purchase.order"].browse(self._context.get("active_id"))
        purchase.ensure_one()
        plan_advance = purchase.invoice_plan_ids.filtered(
            lambda l: l.to_invoice and l.invoice_type == "advance"
        )
        if plan_advance:  # Create advance invoice using percentage
            MakeInvoice = self.env["purchase.advance.payment.inv"]
            makeinv_wizard = {
                "advance_payment_method": "percentage",
                "amount": plan_advance.percent,
            }
            makeinvoice = MakeInvoice.create(makeinv_wizard)
            makeinvoice.with_context(invoice_plan_id=plan_advance.id).create_invoices()
        # Create non-advance invoices
        if self._context.get("all_remain_invoices") or not plan_advance:
            return super().create_invoices_by_plan()
        return {"type": "ir.actions.act_window_close"}
