# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        done_moves = super()._action_done(cancel_backorder=cancel_backorder)
        # ensure received qty is updated on related POs
        for move in done_moves:
            po_line = move.purchase_line_id
            if (
                po_line
                and move.state == "done"
                and po_line.qty_received_method == "stock_moves"
                and po_line.product_qty < 0
            ):
                move.to_refund = True
        return done_moves
