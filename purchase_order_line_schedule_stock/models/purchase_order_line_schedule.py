# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class PurchaseOrderLineSchedule(models.Model):

    _inherit = "purchase.order.line.schedule"

    @api.depends("order_line_id.qty_received")
    def _compute_qty_received(self):
        # We really don't care about the relation between the stock move
        # and the schedule line. We allocate all the received quantity
        # from stock moves into the schedule lines by allocating first the older
        # schedule lines.
        super(PurchaseOrderLineSchedule, self)._compute_qty_received()
        for ol in self.mapped("order_line_id").filtered(
            lambda line: line.qty_received_method == "stock_moves"
        ):
            ol._compute_qty_received()
            qty_to_allocate = ol.qty_received
            for sl in ol.schedule_line_ids.sorted(lambda x: x.date_planned):
                sl.qty_received = min(sl.product_qty, qty_to_allocate)
                qty_to_allocate -= sl.qty_received
