# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models


class SchedulePurchaseOrder(models.TransientModel):

    _name = "schedule.purchase.order"
    _description = "Wizard To Schedule a Purchase Order"

    order_id = fields.Many2one(comodel_name="purchase.order", required=True)
    schedule_date_ids = fields.One2many(
        comodel_name="schedule.purchase.order.date", inverse_name="wiz_id"
    )

    def _prepare_schedule_purchase_order_dates(self, dp, date_planned):
        return {
            "date_planned": dp,
            "schedule_line_ids": [(6, 0, date_planned[dp])],
            "count_schedule_lines": len(date_planned[dp]),
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context["active_model"]
        assert active_model == "purchase.order", "Bad context propagation"
        if "order_id" in res:
            order = self.env["purchase.order"].browse(res["order_id"])
            schedule_dates = []
            date_planned = {}
            for sl in order.order_line.mapped("schedule_line_ids"):
                if sl.date_planned not in date_planned.keys():
                    date_planned[sl.date_planned] = [sl.id]
                else:
                    date_planned[sl.date_planned].append(sl.id)
            for dp in date_planned.keys():
                schedule_dates.append(
                    [
                        0,
                        0,
                        self._prepare_schedule_purchase_order_dates(dp, date_planned),
                    ]
                )
            res["schedule_date_ids"] = schedule_dates
        return res

    def create_schedule_grid(self):
        self.ensure_one()

        # 2d matrix widget need real records to work
        grid = self.env["schedule.purchase.order.grid"].create({"wiz_id": self.id})
        grid._onchange_wiz_id()
        res = {
            "name": _("Schedule Grid"),
            "src_model": "schedule.purchase.order",
            "view_mode": "form",
            "target": "new",
            "res_model": "schedule.purchase.order.grid",
            "res_id": grid.id,
            "type": "ir.actions.act_window",
        }
        return res


class SchedulePurchaseOrderDate(models.TransientModel):
    _name = "schedule.purchase.order.date"
    _description = "Wizard to manage schedule order dates"

    wiz_id = fields.Many2one(comodel_name="schedule.purchase.order", required=True)
    date_planned = fields.Datetime(string="Scheduled Date", required=True)
    schedule_line_ids = fields.Many2many(comodel_name="purchase.order.line.schedule")
    count_schedule_lines = fields.Integer(
        string="# Lines", compute="_compute_count_schedule_lines"
    )

    @api.onchange("schedule_line_ids")
    def onchange_schedule_line_ids(self):
        if self.schedule_line_ids:
            self.date_planned = self.schedule_line_ids[0].date_planned

    def _compute_count_schedule_lines(self):
        for rec in self:
            rec.count_schedule_lines = len(rec.schedule_line_ids)
