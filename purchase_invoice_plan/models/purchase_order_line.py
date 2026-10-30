# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _is_invoice_plan_line(self):
        """Order lines billed by installments of the invoice plan"""
        self.ensure_one()
        return (
            self.order_id.use_invoice_plan
            and not self.display_type
            and not self.is_downpayment
        )

    def _get_purchase_invoice_plan(self, move=False):
        """Installment to bill for this order line: the one being billed by
        "Create Bill by Plan", the one already used by the bill, or the next
        pending installment."""
        self.ensure_one()
        order = self.order_id
        if (
            not order.use_invoice_plan
            or self.display_type
            or (move and move.move_type != "in_invoice")
        ):
            return self.env["purchase.invoice.plan"]
        invoice_plan_id = self.env.context.get("invoice_plan_id")
        if invoice_plan_id:
            plan = self.env["purchase.invoice.plan"].browse(invoice_plan_id)
            return plan if plan.purchase_id == order else plan.browse()
        if move:
            return move._get_purchase_invoice_plan(order)
        return order._get_next_invoice_plan()

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move=move)
        plan = self._get_purchase_invoice_plan(move=move)
        if not plan:
            return res
        quantity = res["quantity"]
        if not self.env.context.get("from_edi"):
            # Quantities of an imported vendor document are kept as is
            if self.is_downpayment:
                quantity = plan._get_downpayment_line_quantity(self, quantity)
            else:
                quantity = plan._get_invoice_line_quantity(self, quantity)
            if res.get("balance") and res["quantity"]:
                # purchase_stock computes the balance for the full quantity
                res["balance"] = res["balance"] * quantity / res["quantity"]
            res["quantity"] = quantity
        # Down payment deductions are not part of the installment amount
        if not self.is_downpayment and self.uom_id.compare(quantity, 0) > 0:
            res["purchase_invoice_plan_id"] = plan.id
        return res
