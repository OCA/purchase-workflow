# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class SchedulePurchaseOrderGrid(models.TransientModel):
    _name = "schedule.purchase.order.grid"
    _description = "Schedule Purchase Order Grid"

    wiz_id = fields.Many2one(comodel_name="schedule.purchase.order",)
    line_ids = fields.Many2many(comodel_name="schedule.grid.line")

    @api.onchange("wiz_id")
    def _onchange_wiz_id(self):
        lines = []
        for schedule_date in self.wiz_id.schedule_date_ids:
            for ol in self.wiz_id.order_id.order_line:
                schedule_lines = schedule_date.schedule_line_ids.filtered(
                    lambda sl: sl.order_line_id == ol
                )
                if schedule_lines:
                    for schedule_line in schedule_lines:
                        lines.append(
                            [
                                0,
                                0,
                                self._get_default_grid_line(
                                    ol, schedule_date, schedule_line
                                ),
                            ]
                        )
                else:
                    schedule_line = self.env["purchase.order.line.schedule"]
                    lines.append(
                        [
                            0,
                            0,
                            self._get_default_grid_line(
                                ol, schedule_date, schedule_line
                            ),
                        ]
                    )
        self.line_ids = lines

    def _get_default_grid_line(self, order_line, schedule_date, schedule_line):
        to_schedule_qty = (
            schedule_line
            and (
                schedule_line.product_qty
                - schedule_line.qty_in_receipt
                - schedule_line.qty_received
            )
            or 0.0
        )
        values = {
            "value_x": schedule_date.date_planned,
            "value_y": order_line.name,
            "product_qty": to_schedule_qty,
            "schedule_line_id": schedule_line and schedule_line.id or False,
            "date_planned": schedule_date.date_planned,
            "order_line_id": order_line.id,
            "qty_received": schedule_line and schedule_line.qty_received or 0.0,
            "qty_in_receipt": schedule_line and schedule_line.qty_in_receipt or 0.0,
        }
        return values

    def update_schedule_lines(self):
        self.ensure_one()
        for ol in self.wiz_id.order_id.order_line:
            order_line = ol.with_context(skip_auto_update_schedule_lines=True)
            order_line.schedule_line_ids = [(5, 0, 0)]
            schedule_lines_data = []
            for line in self.line_ids.filtered(lambda l: l.order_line_id == ol):
                if line.product_qty or line.qty_received or line.qty_in_receipt:
                    schedule_lines_data.append(
                        [0, 0, line._prepare_schedule_line_data()]
                    )
            order_line.schedule_line_ids = schedule_lines_data
        return {"type": "ir.actions.act_window_close"}


class SchedulePurchaseOrderGridLine(models.TransientModel):
    _name = "schedule.grid.line"
    _description = "Schedule Purchase Order Grid Line"

    order_line_id = fields.Many2one(comodel_name="purchase.order.line")
    schedule_line_id = fields.Many2one(comodel_name="purchase.order.line.schedule")
    date_planned = fields.Datetime("Scheduled Date")
    value_x = fields.Char(string="Scheduled Date")
    value_y = fields.Char(string="Order Line")
    product_qty = fields.Float(string="Quantity", digits="Product Unit of Measure")
    qty_received = fields.Float()
    qty_in_receipt = fields.Float()

    def _prepare_schedule_line_data(self):
        self.ensure_one()
        return {
            "date_planned": self.date_planned,
            "product_qty": self.product_qty + self.qty_in_receipt + self.qty_received,
            "qty_received": self.qty_received,
        }
