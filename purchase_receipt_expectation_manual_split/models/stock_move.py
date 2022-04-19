# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_cancel(self):
        moves_to_cancel = self.filtered(lambda m: m.state != "cancel")
        res = super()._action_cancel()
        for move in moves_to_cancel:
            if move.purchase_line_id:
                move.purchase_line_id._merge_back_into_original_line(
                    move.product_uom._compute_quantity(
                        move.product_qty, move.purchase_line_id.product_uom
                    )
                )
        return res
