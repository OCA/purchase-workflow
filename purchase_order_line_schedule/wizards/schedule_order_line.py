# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ScheduleOrderLine(models.TransientModel):

    _name = "schedule.order.line"
    _description = "Wizard To Schedule Order Lines for a Purchase Order Line"

    order_line_id = fields.Many2one(comodel_name="purchase.order.line", required=True,)
    item_ids = fields.One2many(
        comodel_name="schedule.order.line.item", inverse_name="wiz_id", string="Items",
    )

    def _prepare_item(self, sl):
        return {
            "date_planned": sl.date_planned,
            "product_qty": sl.product_qty,
            "qty_received": sl.qty_received,
            "purchase_state": sl.order_line_id.order_id.state,
            "qty_to_receive": sl.product_qty - sl.qty_received,
            "product_id": sl.product_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context["active_model"]
        assert active_model == "purchase.order.line", "Bad context propagation"
        if "order_line_id" in res:
            ol = self.env["purchase.order.line"].browse(res["order_line_id"])
            items = []
            for sl in ol.schedule_line_ids:
                items.append([0, 0, self._prepare_item(sl)])
            res["item_ids"] = items
        return res

    def update_schedule_lines(self):
        self.ensure_one()
        line = self.order_line_id.with_context(skip_auto_update_schedule_lines=True)
        line.schedule_line_ids = [(5, 0, 0)]
        for item in self.item_ids:
            line.schedule_line_ids = [
                (
                    0,
                    0,
                    {
                        "date_planned": item.date_planned,
                        "product_qty": item.product_qty,
                        "qty_received": item.qty_received,
                    },
                )
            ]
        return {"type": "ir.actions.act_window_close"}


class ScheduleOrderLineItem(models.TransientModel):

    _name = "schedule.order.line.item"
    _description = "Wizard To Schedule Order Lines for a Purchase Order Line"
    _order = "date_planned, id"

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
    qty_received = fields.Float("Received", digits="Product Unit of Measure",)
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
            line.qty_to_receive = line.product_qty - line.qty_received
