# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _deduce_qty(self, qty_to_remove, rounding):
        """Deduce the provided qty with respect to done qties."""
        self = self.with_context(do_not_unreserve=True)
        for move in self:
            if float_is_zero(qty_to_remove, precision_rounding=rounding):
                break
            # we cannot deduce more than the "not done" qty
            removable_qty = move._get_removable_qty()
            # If removable_qty <= qty_to_remove, deduce removable_qty
            if (
                float_compare(removable_qty, qty_to_remove, precision_rounding=rounding)
                < 1
            ):
                move.product_uom_qty -= removable_qty
                qty_to_remove -= removable_qty
            # Else, deduce qty_to_remove from it
            else:
                move.product_uom_qty -= qty_to_remove
                qty_to_remove = 0
            # if new move product_uom_qty is 0, cancel it
            if float_is_zero(move.product_uom_qty, precision_rounding=rounding):
                move._action_cancel()

    def _get_removable_qty(self):
        moves = self.filtered(
            lambda move: move.location_dest_id.usage != "supplier"
            and (
                not move.origin_returned_move_id
                or (move.origin_returned_move_id and move.to_refund)
            )
        )
        assert (
            len(set(moves.mapped("product_uom"))) == 1
        ), "moves doesn't share the same UoM"
        return sum([move.product_uom_qty - move.quantity_done for move in moves])
