# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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
