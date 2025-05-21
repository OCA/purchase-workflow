# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_received = fields.Boolean(
        compute="_compute_force_received",
        inverse="_inverse_force_received",
        store=True,
        tracking=True,
        help="If true, the order is marked forced only when all lines are fully received"
        " and at least one line was manually forced.",
    )

    @api.depends("order_line.reception_status", "order_line.force_received")
    def _compute_force_received(self):
        for po in self:
            all_received = all(
                line.reception_status == "received" for line in po.order_line
            )
            any_forced = any(line.force_received for line in po.order_line)
            po.force_received = all_received and any_forced

    def _inverse_force_received(self):
        for po in self:
            if po.force_received:
                to_force = po.order_line.filtered(
                    lambda l: l.reception_status != "received"
                )
                to_force.write({"force_received": True})
            else:
                forced_lines = po.order_line.filtered(lambda l: l.force_received)
                forced_lines.write({"force_received": False})
                forced_lines._compute_reception_status()

    @api.depends(
        "state",
        "force_received",
        "order_line.qty_received",
        "order_line.product_qty",
        "order_line.force_received",
        "order_line.reception_status",
    )
    def _compute_reception_status(self):
        result = super()._compute_reception_status()
        for order in self.filtered(lambda po: po.reception_status != "received"):
            status = order.reception_status
            if order.state in ("purchase", "done"):
                if all(
                    [line.reception_status == "received" for line in order.order_line]
                ):
                    status = "received"
                elif any(
                    [
                        line.reception_status in ["received", "partial"]
                        for line in order.order_line
                    ]
                ):
                    status = "partial"
            order.reception_status = status
        return result
