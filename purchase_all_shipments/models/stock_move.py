# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_reception_chain_moves(self):
        """Recursively get the destination moves that continue the reception.

        Moves pushed by the reception route are part of it, while moves pulled
        by the demand of another document are not.
        """
        res = self.move_dest_ids.filtered(lambda m: m.rule_id.action == "push")
        if res:
            res |= res._get_reception_chain_moves()
        return res
