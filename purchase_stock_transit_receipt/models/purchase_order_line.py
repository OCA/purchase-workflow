# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "move_ids.move_dest_ids.state",
        "move_ids.move_dest_ids.quantity",
        "move_ids.move_dest_ids.returned_move_ids.state",
        "move_ids.move_dest_ids.returned_move_ids.quantity",
        "move_ids.move_dest_ids.returned_move_ids.returned_move_ids.state",
        "move_ids.move_dest_ids.returned_move_ids.returned_move_ids.quantity",
    )
    def _compute_qty_received(self):
        return super()._compute_qty_received()

    def _get_po_line_moves(self):
        moves = super()._get_po_line_moves()
        transit_locations = self.env[
            "stock.warehouse"
        ]._get_incoming_transit_locations()
        transit_moves = moves.filtered(
            lambda move: move.location_id in transit_locations
            or move.location_dest_id in transit_locations
        )
        if not transit_moves:
            return moves
        physical_moves = transit_moves.move_dest_ids.filtered(
            lambda move: not move.origin_returned_move_id
            and move.location_id in transit_locations
        )
        returns = physical_moves.returned_move_ids
        physical_moves |= returns | returns.returned_move_ids
        if self.env.context.get("accrual_entry_date"):
            physical_moves = physical_moves.filtered(
                lambda move: fields.Date.context_today(move, move.date)
                <= self.env.context["accrual_entry_date"]
            )
        return (moves - transit_moves) | physical_moves
