# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    next_bill_method = fields.Selection(
        selection=[
            ("auto", "Next bill by sequence"),
            ("manual", "Next bill by manual selection"),
        ],
        help="Saved default method for this order",
    )


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    "%s %s : %s -- %s%s -- %s"
                    % (
                        _("Installment"),
                        rec.installment,
                        rec.plan_date,
                        rec.percent,
                        "%",
                        "{:,.2f}".format(rec.amount),
                    ),
                )
            )
        return result

    def _get_plan_qty(self, order_line, percent):
        """If manual select installment, use it for qty"""
        plan_qty = super()._get_plan_qty(order_line, percent)
        if self.env.context.get("next_bill_method") == "manual":
            res = list(
                filter(
                    lambda l: l["order_line_id"] == order_line.id,
                    self.env.context["invoice_qty_line_ids"],
                )
            )
            if res:
                plan_qty = res[0].get("quantity")
            else:
                plan_qty = 0
        return plan_qty

    def _is_final(self):
        """Manual selection not considered final, to enforce selected qty"""
        if self.env.context.get("next_bill_method"):
            return False
        return super()._is_final()
