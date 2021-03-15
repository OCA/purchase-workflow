# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PurchaseOrderLineSchedule(models.Model):

    _name = "purchase.order.line.schedule"
    _description = "Purchase Order Line Schedule"
    _order = "order_line_id, date_planned, id"

    order_id = fields.Many2one(
        comodel_name="purchase.order", related="order_line_id.order_id", store=True
    )
    purchase_state = fields.Selection(related="order_line_id.order_id.state",)
    qty_received_method = fields.Selection(related="order_line_id.qty_received_method",)
    order_line_id = fields.Many2one(
        comodel_name="purchase.order.line", required=True, ondelete="cascade"
    )
    date_planned = fields.Datetime(string="Scheduled Date", index=True, required=True)
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=True
    )
    qty_received = fields.Float(
        "Received",
        compute="_compute_qty_received",
        inverse="_inverse_qty_received",
        compute_sudo=True,
        digits="Product Unit of Measure",
    )
    qty_to_receive = fields.Float(
        "To Receive",
        compute="_compute_qty_to_receive",
        compute_sudo=True,
        digits="Product Unit of Measure",
    )
    qty_received_manual = fields.Float(
        "Manual Received Qty", digits="Product Unit of Measure", copy=False
    )
    product_id = fields.Many2one(
        comodel_name="product.product", related="order_line_id.product_id", store=True,
    )
    company_id = fields.Many2one(
        "res.company", related="order_line_id.company_id", store=True
    )

    @api.depends("qty_received", "product_qty")
    def _compute_qty_to_receive(self):
        for line in self:
            line.qty_to_receive = line.product_qty - line.qty_received

    @api.depends(
        "product_qty", "qty_received_manual", "order_line_id.qty_received_method"
    )
    def _compute_qty_received(self):
        for line in self:
            if line.order_line_id.qty_received_method == "manual":
                line.qty_received = line.qty_received_manual or 0.0
            else:
                line.qty_received = 0.0

    @api.onchange("qty_received")
    def _inverse_qty_received(self):
        for line in self:
            if line.order_line_id.qty_received_method == "manual":
                line.qty_received_manual = line.qty_received
            else:
                line.qty_received_manual = 0.0

    def _update_order_line_date_planned(self):
        order_lines = self.mapped("order_line_id")
        for ol in order_lines:
            ol.date_planned = max(ol.schedule_line_ids.mapped("date_planned"))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrderLineSchedule, self).create(vals_list)
        res._update_order_line_date_planned()
        return res

    def write(self, values):
        res = super(PurchaseOrderLineSchedule, self).write(values)
        self._update_order_line_date_planned()
        return res
