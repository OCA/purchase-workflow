# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_invoiced = fields.Boolean(
        compute="_compute_force_invoiced",
        inverse="_inverse_force_invoiced",
        store=True,
        tracking=True,
        help="If true, the order is marked forced only "
        "when all lines are fully invoiced"
        " and at least one line was manually forced.",
    )

    @api.depends("order_line.invoice_status", "force_invoiced")
    def _get_invoiced(self):
        super()._get_invoiced()
        for order in self:
            if not order.order_line:
                order.invoice_status = "no"
                continue
            if order.force_invoiced:
                order.invoice_status = "invoiced"
                continue
            if any(line.invoice_status == "to invoice" for line in order.order_line):
                order.invoice_status = "to invoice"
            elif all(
                line.invoice_status == "invoiced"
                for line in order.order_line.filtered(
                    lambda line: not line.display_type
                )
            ):
                order.invoice_status = "invoiced"
            else:
                order.invoice_status = "no"
        return True

    @api.depends("order_line.invoice_status", "order_line.force_invoiced")
    def _compute_force_invoiced(self):
        for po in self:
            po.order_line._compute_invoice_status()
            non_display_lines = po.order_line.filtered(
                lambda line: not line.display_type
            )
            all_invoiced = all(
                line.invoice_status == "invoiced" for line in non_display_lines
            )
            any_forced = any(line.force_invoiced for line in non_display_lines)
            po.force_invoiced = all_invoiced and any_forced

    def _inverse_force_invoiced(self):
        for po in self:
            if po.force_invoiced:
                to_force = po.order_line.filtered(
                    lambda line: line.invoice_status != "invoiced"
                )
                to_force.write({"force_invoiced": True})
            else:
                forced_lines = po.order_line.filtered(lambda line: line.force_invoiced)
                forced_lines.write({"force_invoiced": False})
                forced_lines._compute_invoice_status()
