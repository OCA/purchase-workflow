# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    factory_calendar_id = fields.Many2one(comodel_name="resource.calendar")
    delay_calendar_type = fields.Selection(
        [("natural", "Natural days"), ("supplier_calendar", "Supplier Calendar")],
        default="natural",
        required=True,
    )

    @api.onchange("delay_calendar_type")
    def _onchange_delay_calendar_type(self):
        for rec in self:
            if rec.delay_calendar_type == "natural":
                rec.factory_calendar_id = False

    def supplier_plan_days(self, date_from, delta):
        """Helper method to calculate supplier delay based on its
        working days (if set).

        :param datetime date_from: reference date.
        :param integer delta: delay established.
        :return: datetime: resulting date.
        """
        self.ensure_one()
        if not isinstance(date_from, datetime):
            date_from = fields.Datetime.to_datetime(date_from)
        if delta == 0:
            return date_from
        if self.factory_calendar_id:
            if delta < 0:
                # We force the date planned to be at the beginning of the day.
                # So no work intervals are found in the reference date.
                dt_planned = date_from.replace(hour=0)
            else:
                # We force the date planned at the end of the day.
                dt_planned = date_from.replace(hour=23)
            date_result = self.factory_calendar_id.plan_days(
                delta, dt_planned, compute_leaves=True
            )
        else:
            date_result = date_from + timedelta(days=delta)
        return date_result
