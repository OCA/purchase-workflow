# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _update_value_order_from_rfq(self, order):
        order = super()._update_value_order_from_rfq(order)
        if self.use_invoice_plan:
            invoice_plans = []
            for plan in self.invoice_plan_ids:
                vals = {
                    "installment": plan.installment,
                    "plan_date": plan.plan_date,
                    "invoice_type": plan.invoice_type,
                    "percent": plan.percent,
                }
                invoice_plans.append((0, 0, vals))
            order.write(
                {
                    "use_invoice_plan": self.use_invoice_plan,
                    "invoice_plan_ids": invoice_plans,
                }
            )
        return order
