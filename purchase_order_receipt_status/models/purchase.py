# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_status = fields.Selection(
        [
            ("nothing", "Nothing to receive"),
            ("pending", "Not Received"),
            ("partial", "Partially Received"),
            ("partial_no_backorder", "Partially Received (No Backorder)"),
            ("full", "Fully Received"),
        ],
        compute="_compute_receipt_status",
        store=True,
    )

    @api.depends(
        "picking_ids",
        "picking_ids.state",
        "order_line.qty_received",
        "order_line.product_qty",
    )
    def _compute_receipt_status(self):
        for order in self:
            if not order.picking_ids or all(
                pick.state == "cancel" for pick in order.picking_ids
            ):
                status = "nothing"
            elif all(
                line.qty_received >= line.product_qty for line in order.order_line
            ):
                status = "full"
            elif all(
                float_is_zero(
                    line.qty_received, precision_rounding=line.product_uom.rounding
                )
                for line in order.order_line
            ):
                status = "pending"
            elif order.is_shipped:
                status = "partial_no_backorder"
            else:
                status = "partial"
            order.receipt_status = status
