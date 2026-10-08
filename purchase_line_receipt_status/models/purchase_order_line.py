# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    # A better name would be "receipt_status", but it would conflict with
    # purchase_reception_status_line module if both are installed together.
    # We also could have used "receipt_progress", but this name breaks
    # the implicit link with the receipt_status field defined in
    # purchase_reception_status_line which is computed from the same logic.
    line_receipt_status = fields.Selection(
        [
            ("pending", "Not Received"),
            ("partial", "Partially Received"),
            ("full", "Fully Received"),
        ],
        string="Receipt Status",
        compute="_compute_receipt_status",
        store=True,
        readonly=False,
        help=(
            "Indicates the progress of the reception flow for this purchase line. "
            "Computed from incoming stock moves."
        ),
    )

    @api.depends("move_ids", "move_ids.state", "qty_received")
    def _compute_receipt_status(self):
        for line in self:
            line_receipt_status = False
            # consider only incoming moves
            incoming_moves = line.move_ids.filtered(
                lambda m: m.picking_type_id.code == "incoming"
            )

            open_moves = incoming_moves.filtered(
                lambda m: m.state not in ("cancel", "done")
            )

            if not incoming_moves or all(m.state == "cancel" for m in incoming_moves):
                line_receipt_status = False
            elif line.qty_received == 0 and open_moves:
                line_receipt_status = "pending"
            elif open_moves:
                line_receipt_status = "partial"
            else:
                line_receipt_status = "full"
            if line.line_receipt_status != line_receipt_status:
                line.line_receipt_status = line_receipt_status
