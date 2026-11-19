# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_move_dest_ids(self):
        """Recursively get all destination moves with cycle protection"""
        visited = set()

        def _get_dest_recursive(moves):
            result = self.env["stock.move"]
            for move in moves:
                if move.id not in visited:
                    visited.add(move.id)
                    dest_moves = move.move_dest_ids
                    result |= dest_moves
                    if dest_moves:
                        result |= _get_dest_recursive(dest_moves)
            return result

        return _get_dest_recursive(self.filtered("move_dest_ids"))
