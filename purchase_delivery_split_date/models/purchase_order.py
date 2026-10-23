# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from itertools import groupby

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_split_pickings(self):
        # Avoid one search query per order
        purchases_moves = self.env["stock.move"].search(
            [
                ("purchase_line_id", "in", self.order_line.ids),
                ("state", "not in", ("cancel", "done")),
            ]
        )
        for order in self:
            order_line_ids = set(order.order_line.ids)
            order_moves = purchases_moves.filtered(
                lambda move: move.purchase_line_id.id in order_line_ids
            )
            pickings = order_moves.mapped("picking_id")
            # A receipt, a return and a dropship of the same order are split on
            # their own: a move only goes to a picking of its own kind.
            moves_by_kind = defaultdict(lambda: self.env["stock.move"])
            for move in order_moves:
                picking = move.picking_id
                kind = (
                    picking.picking_type_id,
                    picking.location_id,
                    picking.location_dest_id,
                )
                moves_by_kind[kind] |= move
            # Moves to shift, per target picking and date, so that they are
            # unreserved, moved and reserved again once per order.
            moves_by_target = defaultdict(lambda: self.env["stock.move"])
            for moves in moves_by_kind.values():
                pickings_by_date = {}
                for pick in moves.mapped("picking_id"):
                    pickings_by_date[pick.scheduled_date.date()] = pick
                order_lines = moves.mapped("purchase_line_id")
                date_groups = groupby(
                    order_lines, lambda l: l._get_group_keys(l.order_id, l)
                )
                for key, lines in date_groups:
                    date_key = fields.Date.from_string(key[0]["date_planned"])
                    for line in lines:
                        for move in line.move_ids & moves:
                            if (
                                move.picking_id.scheduled_date.date() != date_key
                                or pickings_by_date.get(date_key) != move.picking_id
                            ):
                                if date_key not in pickings_by_date:
                                    copy_vals = line._first_picking_copy_vals(key, line)
                                    new_picking = move.picking_id.sudo().copy(copy_vals)
                                    pickings_by_date[date_key] = new_picking
                                moves_by_target[
                                    (pickings_by_date[date_key], date_key)
                                ] |= move
            if moves_by_target:
                shifted_moves = self.env["stock.move"].concat(*moves_by_target.values())
                shifted_moves._do_unreserve()
                for (picking, date_key), target_moves in moves_by_target.items():
                    target_moves.write(
                        {
                            "picking_id": picking.id,
                            "date_deadline": date_key,
                            "date": date_key,
                        }
                    )
                shifted_moves._action_assign()
            pickings.filtered(lambda picking: not picking.move_ids).write(
                {"state": "cancel"}
            )
