# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models
from odoo.tools import float_compare, float_is_zero


def equal(x, y, rounding):
    return float_is_zero(x - y, precision_rounding=rounding)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, values):
        res = super().write(values)
        if "product_qty" in values or "product_uom" in values:
            self._propagage_qty_to_moves()
        return res

    def _propagage_qty_to_moves(self):
        for line in self:
            if line.state != "purchase":
                continue
            rounding = line.product_uom.rounding
            for move in line.move_dest_ids:
                if move.state in ("cancel", "done"):
                    continue
                if move.product_id != line.product_id:
                    continue
                move.product_uom_qty = line.product_uom_qty
                if float_is_zero(move.product_uom_qty, precision_rounding=rounding):
                    move._action_cancel()
            moves_done = line.move_ids.filtered(lambda r: r.state == "done")
            qty_done = sum(moves_done.mapped("product_uom_qty"))
            moves = line.move_ids.filtered(lambda r: r.state not in ("cancel", "done"))
            previous_qty = sum(moves.mapped("product_uom_qty"))
            new_qty = line.product_uom_qty
            # If the new qty equals the already received qty, cancel remaining moves
            if qty_done and equal(qty_done, new_qty, rounding):
                moves._action_cancel()
                continue
            # Do nothing is qty has been increased, since odoo handles this case
            if new_qty >= previous_qty:
                continue
            # If qty has been decreased, cancel full moves if possible
            moves = moves.filtered_domain(
                [
                    ("state", "not in", ("cancel", "done")),
                    ("product_id", "=", line.product_id.id),
                ]
            ).sorted(lambda m: (m.product_uom_qty, m.quantity_done))
            qty_to_remove = previous_qty - new_qty
            removable_qty = moves._get_removable_qty()
            if (
                float_compare(qty_to_remove, removable_qty, precision_rounding=rounding)
                == 1
            ):
                exception_text = _(
                    "You cannot remove more that what remains to be done. "
                    "Max removable quantity {}."
                ).format(removable_qty)
                raise exceptions.UserError(exception_text)
            moves._deduce_qty(qty_to_remove, rounding)
