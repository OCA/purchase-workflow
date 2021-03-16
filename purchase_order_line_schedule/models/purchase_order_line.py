# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    schedule_line_ids = fields.One2many(
        comodel_name="purchase.order.line.schedule",
        inverse_name="order_line_id",
        string="Delivery Schedule",
    )
    has_schedule_lines = fields.Boolean(compute="_compute_has_schedule_lines")
    qty_to_schedule = fields.Float(
        string="To Schedule", compute="_compute_qty_to_schedule"
    )

    @api.depends("product_qty", "schedule_line_ids", "schedule_line_ids.product_qty")
    def _compute_qty_to_schedule(self):
        for line in self:
            line.qty_to_schedule = line.product_qty - sum(
                line.schedule_line_ids.mapped("product_qty")
            )

    @api.depends("schedule_line_ids")
    def _compute_has_schedule_lines(self):
        for line in self:
            line.has_schedule_lines = line.schedule_line_ids and True or False

    @api.depends("schedule_line_ids", "schedule_line_ids.qty_received")
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self:
            if line.schedule_line_ids:
                line.qty_received = sum(
                    sl.qty_received for sl in line.schedule_line_ids
                )

    @api.onchange("qty_received")
    def _inverse_qty_received(self):
        for line in self:
            if line.qty_received_method == "manual":
                qty_to_allocate = line.qty_received
                for sl in line.schedule_line_ids.sorted(lambda x: x.date_planned):
                    sl.qty_received = min(sl.product_qty, qty_to_allocate)
                    qty_to_allocate -= sl.qty_received_manual
            else:
                super(PurchaseOrderLine, line)._inverse_qty_received()

    def action_open_schedule_lines(self):
        context = dict(self.env.context)
        context.update(default_order_line_id=self.id)
        return {
            "name": _("Schedule Lines"),
            "type": "ir.actions.act_window",
            "res_model": "schedule.order.line",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def _update_schedule_lines(self):
        if self.env.context.get("skip_auto_update_schedule_lines", False):
            return True
        for rec in self:
            sls = rec.schedule_line_ids
            if not sls:
                vals = {
                    "date_planned": rec.date_planned,
                    "product_qty": rec.product_qty,
                    "order_line_id": rec.id,
                }
                rec.schedule_line_ids = [(0, 0, vals)]
            else:
                qty = sum(rec.schedule_line_ids.mapped("product_qty"))
                # Update the last scheduled date of the schedule lines
                # And update the quantity of schedule lines so as to match
                # that of the purchase order line.
                for sl in sls.sorted(lambda x: x.date_planned, reverse=True):
                    if qty != rec.product_qty:
                        sl.product_qty += rec.product_qty - qty
                    if sl.date_planned != rec.date_planned:
                        sl.date_planned = rec.date_planned
                    break

    @api.model_create_multi
    def create(self, vals_list):
        recs = super(PurchaseOrderLine, self).create(vals_list)
        recs._update_schedule_lines()
        return recs

    def write(self, values):
        res = super(PurchaseOrderLine, self).write(values)
        self._update_schedule_lines()
        return res
