# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    factory_calendar_id = fields.Many2one(comodel_name="resource.calendar")
    delay_calendar_type = fields.Selection(
        [
            ("natural", "Natural days"),
            ("supplier_calendar", "Specific Supplier Calendar"),
            ("company_calendar", "Default Supplier Calendar"),
        ],
        default="natural",
        required=True,
        help="Natural days: the lead time counts every day.\n"
        "Specific Supplier Calendar: the lead time counts the working days of the "
        "Factory Calendar of the vendor.\n"
        "Default Supplier Calendar: the lead time counts the working days of the "
        "calendar set in the purchase settings, or every day if none is set.",
    )

    @api.model
    def default_get(self, fields):
        """New contacts use the default supplier calendar of the company."""
        res = super().default_get(fields)
        if (
            res.get("delay_calendar_type") == "natural"
            and "default_delay_calendar_type" not in self.env.context
            and self.env.company.supplier_calendar_id
        ):
            res["delay_calendar_type"] = "company_calendar"
        return res

    @api.onchange("delay_calendar_type")
    def _onchange_delay_calendar_type(self):
        for rec in self:
            if rec.delay_calendar_type != "supplier_calendar":
                rec.factory_calendar_id = False

    def _get_supplier_calendar(self, company=None):
        """The calendar the lead time of the vendor is counted in, if any."""
        self.ensure_one()
        if self.delay_calendar_type == "company_calendar":
            return (company or self.env.company).supplier_calendar_id
        return self.factory_calendar_id

    def supplier_plan_days(self, date_from, delta, company=None):
        """Helper method to calculate supplier delay based on its
        working days (if set).

        :param datetime date_from: reference date.
        :param integer delta: delay established.
        :param company: company whose default supplier calendar is used.
        :return: datetime: resulting date.
        """
        self.ensure_one()
        if isinstance(delta, float):
            delta = round(delta)
        if not isinstance(date_from, datetime):
            date_from = fields.Datetime.to_datetime(date_from)
        if delta == 0:
            return date_from
        calendar = self._get_supplier_calendar(company)
        if calendar:
            if delta < 0:
                # We force the date planned to be at the beginning of the day.
                # So no work intervals are found in the reference date.
                dt_planned = date_from.replace(hour=0)
            else:
                # We force the date planned at the end of the day.
                dt_planned = date_from.replace(hour=23)
            date_result = calendar.plan_days(delta, dt_planned, compute_leaves=True)
        else:
            date_result = date_from + timedelta(days=delta)
        return date_result
