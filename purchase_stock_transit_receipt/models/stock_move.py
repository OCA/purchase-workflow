# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    transit_move_dest_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_transit_move_rel",
        column1="transit_move_orig_id",
        column2="transit_move_dest_id",
        string="Destination Moves after Transit",
        copy=False,
    )
    transit_move_orig_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_transit_move_rel",
        column1="transit_move_dest_id",
        column2="transit_move_orig_id",
        string="Original Transit Moves",
        copy=False,
    )

    @api.depends("transit_move_orig_ids.date", "transit_move_orig_ids.state")
    def _compute_delay_alert_date(self):
        res = super()._compute_delay_alert_date()
        for move in self.filtered(lambda m: m.state not in ("done", "cancel")):
            transit_date = max(
                move.transit_move_orig_ids.filtered(
                    lambda m: m.state not in ("done", "cancel") and m.date
                ).mapped("date"),
                default=False,
            )
            if transit_date and transit_date > (move.delay_alert_date or move.date):
                move.delay_alert_date = transit_date
        return res

    def _is_purchase_return(self):
        if super()._is_purchase_return():
            return True
        physical_move = self.origin_returned_move_id
        if not (
            self.location_dest_id.usage == "transit"
            and physical_move.location_id.usage == "transit"
            and physical_move.location_dest_id.usage == "internal"
        ):
            return False
        transit_locations = self.env[
            "stock.warehouse"
        ]._get_incoming_transit_locations()
        return (
            self.location_dest_id in transit_locations
            and physical_move.location_id in transit_locations
        )

    def _get_open_transit_move_dests(self):
        return self.transit_move_dest_ids.filtered(
            lambda move: move.state not in ("done", "cancel")
        )

    def _get_moves_to_propagate_date_deadline(self):
        moves = super()._get_moves_to_propagate_date_deadline()
        return moves | self.transit_move_dest_ids | self.transit_move_orig_ids

    def _prepare_move_split_vals(self, qty):
        values = super()._prepare_move_split_vals(qty)
        move_dests = self._get_open_transit_move_dests()
        if move_dests:
            values["transit_move_dest_ids"] = [Command.set(move_dests.ids)]
        return values

    def _merge_moves_fields(self):
        values = super()._merge_moves_fields()
        if self.transit_move_dest_ids:
            values["transit_move_dest_ids"] = [
                Command.link(move.id) for move in self.transit_move_dest_ids
            ]
        return values

    def _action_cancel(self):
        transit_moves = self.filtered(
            lambda move: move.state != "cancel" and move.transit_move_dest_ids
        )
        res = super()._action_cancel()
        for move in transit_moves:
            move_dests = move._get_open_transit_move_dests()
            siblings = (
                move_dests.move_orig_ids | move_dests.transit_move_orig_ids
            ) - move
            if move.propagate_cancel:
                cut_off = all(state == "cancel" for state in siblings.mapped("state"))
            else:
                cut_off = all(
                    state in ("done", "cancel") for state in siblings.mapped("state")
                )
            if cut_off:
                move_dests.procure_method = "make_to_stock"
                move_dests._recompute_state()
        return res
