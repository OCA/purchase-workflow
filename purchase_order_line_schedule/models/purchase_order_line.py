# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


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
        line_ids = []
        for line in self:
            line_ids += line.schedule_line_ids.ids

        domain = [("id", "in", line_ids)]
        context = dict(self.env.context)
        context.update(default_order_line_id=self.id)

        return {
            "name": _("Schedule Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.order.line.schedule",
            "view_mode": "tree,form",
            "target": "current",
            "domain": domain,
            "context": context,
        }

    def _update_schedule_lines(self):
        for rec in self:
            sls = rec.schedule_line_ids
            if not sls:
                vals = {
                    "date_planned": rec.date_planned,
                    "product_qty": rec.product_qty,
                }
                rec.schedule_line_ids = [(0, 0, vals)]
            else:
                # Update the last scheduled date of the schedule lines
                for sl in sls.sorted(lambda x: x.date_planned, reverse=True):
                    if sl.date_planned != rec.date_planned:
                        sl.date_planned = rec.date_planned
                    break

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrderLine, self).create(vals_list)
        self._update_schedule_lines()
        return res

    def write(self, values):
        res = super(PurchaseOrderLine, self).write(values)
        self._update_schedule_lines()
        return res

    @api.constrains("product_qty", "schedule_line_ids")
    def _check_qty_to_schedule_constrains(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for rec in self:
            if (
                float_compare(rec.qty_to_schedule, 0.0, precision_digits=precision)
                == -1
            ):
                raise ValidationError(
                    _(
                        "You cannot have more quantity in schedule lines "
                        "than in the order line."
                    )
                )
