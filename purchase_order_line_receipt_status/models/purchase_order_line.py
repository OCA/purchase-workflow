# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    receipt_status = fields.Selection(
        [
            ("pending", "Not Received"),
            ("partial", "Partially Received"),
            ("full", "Fully Received"),
        ],
        compute="_compute_receipt_status",
        store=True,
    )

    @api.depends("order_id.picking_ids", "qty_received", "product_qty")
    def _compute_receipt_status(self):
        for line in self:
            move_ids = line.move_ids

            # If there is no stock move linked to the purchase order line or all are cancelled
            if not move_ids or all(move.state == "cancel" for move in move_ids):
                status = False
            # If there is at least one stock move linked to the purchase order line
            else:
                # If there is at least one stock move state = "done"
                # and the others are in "cancel"
                if all(
                    move.state == "cancel" or move.state == "done" for move in move_ids
                ):
                    status = "full"
                # If there is at least one stock move state = "done"
                elif any(move.state == "done" for move in move_ids):
                    status = "partial"
                # If there are other cases
                else:
                    status = "pending"
            line.receipt_status = status
