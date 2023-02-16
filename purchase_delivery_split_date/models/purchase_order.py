# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
            moves = purchases_moves.filtered(
                lambda move: move.purchase_line_id.id in order.order_line.ids
            )
            pickings = moves.mapped("picking_id")
            pickings_by_date = {}
            for pick in pickings:
                pickings_by_date[pick.scheduled_date.date()] = pick

            order_lines = moves.mapped("purchase_line_id")
            date_groups = groupby(
                order_lines, lambda l: l._get_group_keys(l.order_id, l)
            )
            for key, lines in date_groups:
                date_key = fields.Date.from_string(key[0]["date_planned"])
                for line in lines:
                    for move in line.move_ids:
                        if move.state in ("cancel", "done"):
                            continue
                        if (
                            move.picking_id.scheduled_date.date() != date_key
                            or pickings_by_date[date_key] != move.picking_id
                        ):
                            if date_key not in pickings_by_date:
                                copy_vals = line._first_picking_copy_vals(key, line)
                                new_picking = move.picking_id.copy(copy_vals)
                                pickings_by_date[date_key] = new_picking
                            move._do_unreserve()
                            move.update(
                                {
                                    "picking_id": pickings_by_date[date_key],
                                    "date_deadline": date_key,
                                }
                            )
                            move._action_assign()
            pickings.filtered(lambda picking: not picking.move_ids).write(
                {"state": "cancel"}
            )
