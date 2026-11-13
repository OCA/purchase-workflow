# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_reception_chain_moves(self):
        """Get the destination moves that continue the reception.

        Moves pushed by the reception route are part of it, while moves pulled
        by the demand of another document are not. The traversal is iterative
        and keeps track of the moves already visited because ``move_dest_ids``
        can form a cyclic graph (e.g. returning a return links the forward and
        backward moves to each other). A naive recursion over such a cycle
        raises RecursionError.
        """
        result = self.env["stock.move"]
        moves_to_visit = self.move_dest_ids.filtered(
            lambda m: m.rule_id.action == "push"
        )
        while moves_to_visit:
            moves_to_visit -= result
            result |= moves_to_visit
            moves_to_visit = moves_to_visit.move_dest_ids.filtered(
                lambda m: m.rule_id.action == "push"
            )
        return result
