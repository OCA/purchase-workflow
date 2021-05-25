# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.make.planned.invoice"
    _description = "Wizard when create invoice by plan"

    def create_invoices_by_plan(self):
        purchase = self.env["purchase.order"].browse(self._context.get("active_id"))
        purchase.ensure_one()
        invoice_plans = (
            self._context.get("all_remain_invoices")
            and purchase.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            or purchase.invoice_plan_ids.filtered("to_invoice")
        )
        for plan in invoice_plans.sorted("installment"):
            purchase.sudo().with_context(
                invoice_plan_id=plan.id
            ).action_create_invoice()
        return {"type": "ir.actions.act_window_close"}
