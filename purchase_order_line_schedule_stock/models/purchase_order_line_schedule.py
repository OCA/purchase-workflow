# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class PurchaseOrderLineSchedule(models.Model):

    _inherit = "purchase.order.line.schedule"

    @api.depends("order_line_id.qty_received")
    def _compute_qty_received(self):
        super(PurchaseOrderLineSchedule, self)._compute_qty_received()
        for ol in self.mapped("order_line_id").filtered(
            lambda l: l.qty_received_method == "stock_moves"
        ):
            for sl in ol.schedule_line_ids:
                sl.qty_received = 0.0
            for move in ol.move_ids.filtered(
                lambda m: m.product_id == ol.product_id
            ).sorted(lambda m: m.date_expected):
                total = 0.0
                ret_move = move.origin_returned_move_id
                if move.state == "done":
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(
                                move.product_uom_qty, ol.product_uom
                            )
                    elif (
                        ret_move
                        and ret_move._is_dropshipped()
                        and not move._is_dropshipped_returned()
                    ):
                        pass
                    elif (
                        move.location_dest_id.usage == "internal"
                        and move.to_refund
                        and move.location_dest_id
                        not in self.env["stock.location"].search(
                            [("id", "child_of", move.warehouse_id.view_location_id.id)]
                        )
                    ):
                        total -= move.product_uom._compute_quantity(
                            move.product_uom_qty, ol.product_uom
                        )
                    else:
                        total += move.product_uom._compute_quantity(
                            move.product_uom_qty, ol.product_uom
                        )
                to_allocate = total
                # Try to allocate first to the schedule lines that match
                # exactly in the date
                for sl in ol.schedule_line_ids.filtered(
                    lambda l: l.date_planned.date() == move.date_expected.date()
                ):
                    qty = min(to_allocate, sl.product_qty - sl.qty_received)
                    sl.qty_received += qty
                    to_allocate -= qty
                # Now try to allocate the remaining qty
                for sl in ol.schedule_line_ids.sorted(lambda l: l.date_planned):
                    qty = min(to_allocate, sl.product_qty - sl.qty_received)
                    sl.qty_received += qty
                    to_allocate -= qty
