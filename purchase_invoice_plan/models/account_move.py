# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_invoice_plan_ids = fields.Many2many(
        comodel_name="purchase.invoice.plan",
        string="Invoice Plans",
        compute="_compute_purchase_invoice_plan_ids",
        help="Installments of invoice plan billed by this bill",
    )

    @api.depends("invoice_line_ids.purchase_invoice_plan_id")
    def _compute_purchase_invoice_plan_ids(self):
        for move in self:
            move.purchase_invoice_plan_ids = (
                move.invoice_line_ids.purchase_invoice_plan_id
            )

    def write(self, vals):
        res = super().write(vals)
        if "move_type" in vals:
            # A bill switched to refund releases its installments, and back
            lines = self.invoice_line_ids.filtered("purchase_line_id")
            lines.filtered(
                lambda ln: (
                    ln.purchase_invoice_plan_id and ln.move_id.move_type != "in_invoice"
                )
            ).purchase_invoice_plan_id = False
            lines._link_purchase_invoice_plan()
        return res

    def _get_purchase_invoice_plan(self, order):
        """Installment of the purchase order billed by this bill, or the next
        pending installment"""
        self.ensure_one()
        return (
            self.invoice_line_ids.purchase_invoice_plan_id.filtered(
                lambda pln: pln.purchase_id == order
            )[:1]
            or order._get_next_invoice_plan()
        )

    def _set_invoice_plan_date(self):
        """Bill date is the installment date, for every flow creating the bill
        from the purchase order. A date already set on the bill is kept."""
        for move in self:
            if move.move_type != "in_invoice" or move.invoice_date:
                continue
            plans = move.invoice_line_ids.purchase_invoice_plan_id
            if plans:
                move.invoice_date = min(plans.mapped("plan_date"))

    def _add_purchase_order_lines(self, purchase_order_lines):
        res = super()._add_purchase_order_lines(purchase_order_lines)
        # Vendor documents (EDI) keep their own date
        if purchase_order_lines and not self.env.context.get("from_edi"):
            self._set_invoice_plan_date()
        return res
