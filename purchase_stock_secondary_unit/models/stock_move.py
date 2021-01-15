# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        res = super()._action_assign()
        if self.env.context.get("secondary_uom_for_update_moves"):
            for move in self:
                move.secondary_uom_id = move.purchase_line_id.secondary_uom_id
                move._compute_secondary_uom_qty()
        return res
