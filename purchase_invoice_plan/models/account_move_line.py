# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_invoice_plan_id = fields.Many2one(
        comodel_name="purchase.invoice.plan",
        string="Invoice Plan",
        index="btree_not_null",
        copy=False,
        domain="[('purchase_id', '=', purchase_order_id)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.filtered("purchase_line_id")._link_purchase_invoice_plan()
        return lines

    def write(self, vals):
        if "purchase_line_id" in vals and "purchase_invoice_plan_id" not in vals:
            # Installment of another purchase order is released before the
            # change, not to fail its check
            order = (
                self.env["purchase.order.line"]
                .browse(vals["purchase_line_id"])
                .order_id
            )
            self.filtered(
                lambda ln: (
                    ln.purchase_invoice_plan_id
                    and ln.purchase_invoice_plan_id.purchase_id != order
                )
            ).purchase_invoice_plan_id = False
        res = super().write(vals)
        if "purchase_line_id" in vals or "quantity" in vals:
            lines = self.filtered("purchase_line_id")
            lines.filtered(
                lambda ln: (
                    ln.purchase_invoice_plan_id
                    and ln.purchase_line_id.uom_id.compare(ln.quantity, 0) <= 0
                )
            ).purchase_invoice_plan_id = False
            lines._link_purchase_invoice_plan()
        return res

    @api.constrains("purchase_invoice_plan_id", "purchase_line_id", "move_id")
    def _check_purchase_invoice_plan(self):
        lines = self.filtered("purchase_invoice_plan_id")
        for line in lines:
            if line.purchase_invoice_plan_id.purchase_id != line.purchase_order_id:
                raise ValidationError(
                    self.env._(
                        "%(plan)s is not an installment of the purchase order "
                        "of bill line %(line)s.",
                        plan=line.purchase_invoice_plan_id.display_name,
                        line=line.display_name,
                    )
                )
        groups = lines.move_id.invoice_line_ids.filtered(
            "purchase_invoice_plan_id"
        ).grouped(lambda ln: (ln.move_id, ln.purchase_order_id))
        for (move, order), group in groups.items():
            if len(group.purchase_invoice_plan_id) > 1:
                raise ValidationError(
                    self.env._(
                        "Bill %(bill)s can bill only one installment of "
                        "purchase order %(order)s.",
                        bill=move.display_name,
                        order=order.display_name,
                    )
                )

    def _is_purchase_invoice_plan_line(self):
        """Bill lines that count for an installment of the invoice plan"""
        self.ensure_one()
        return (
            self.move_id.move_type == "in_invoice"
            and self.display_type == "product"
            and self.purchase_line_id._is_invoice_plan_line()
        )

    def _link_purchase_invoice_plan(self):
        """Link bill lines added from any flow (Bill Matching, vendor bill
        auto-complete, EDI, ...) to the installment of their purchase order.
        All lines of the same order in the same bill share the installment."""
        lines = self.filtered(
            lambda ln: (
                not ln.purchase_invoice_plan_id
                and ln._is_purchase_invoice_plan_line()
                and ln.purchase_line_id.uom_id.compare(ln.quantity, 0) > 0
            )
        )
        groups = lines.grouped(lambda ln: (ln.move_id, ln.purchase_line_id.order_id))
        for (move, order), group in groups.items():
            plan = move._get_purchase_invoice_plan(order)
            if plan:
                group.purchase_invoice_plan_id = plan
