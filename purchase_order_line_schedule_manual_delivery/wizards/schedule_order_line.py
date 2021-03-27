# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ScheduleOrderLine(models.TransientModel):

    _inherit = "schedule.order.line"

    def _prepare_item(self, sl):
        res = super(ScheduleOrderLine, self)._prepare_item(sl)
        res["qty_in_receipt"] = sl.qty_in_receipt
        res["qty_to_receive"] = sl.product_qty - sl.qty_received - sl.qty_in_receipt
        return res


class ScheduleOrderLineItem(models.TransientModel):

    _inherit = "schedule.order.line.item"

    wiz_id = fields.Many2one("schedule.order.line", required=True, ondelete="cascade")

    order_line_id = fields.Many2one(comodel_name="purchase.order.line",)
    order_id = fields.Many2one(
        comodel_name="purchase.order", related="order_line_id.order_id"
    )
    purchase_state = fields.Selection(related="order_line_id.order_id.state",)
    qty_received_method = fields.Selection(related="order_line_id.qty_received_method")
    date_planned = fields.Datetime(string="Scheduled Date")
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=True
    )
    qty_received = fields.Float("Received", digits="Product Unit of Measure")
    qty_in_receipt = fields.Float(
        "In Receipt", digits="Product Unit of Measure", readonly=True
    )
    qty_to_receive = fields.Float(
        "To Receive",
        compute="_compute_qty_to_receive",
        compute_sudo=True,
        digits="Product Unit of Measure",
    )
    product_id = fields.Many2one(
        comodel_name="product.product", related="order_line_id.product_id"
    )

    @api.depends("qty_received", "product_qty")
    def _compute_qty_to_receive(self):
        for line in self:
            line.qty_to_receive = (
                line.product_qty - line.qty_received - line.qty_in_receipt
            )
