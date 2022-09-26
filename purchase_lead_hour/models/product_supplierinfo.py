# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # In odoo core, we can only set an amount of days,
    # which could not be accurate enough.
    delay_hour = fields.Integer("Delivery Lead Time Hour")

    def _get_next_availability_date(self):
        return fields.Datetime.now()

    def _get_delay_days(self):
        delay_days = super()._get_delay_days()
        delay_hours = self.delay_hour / 24
        return delay_days + delay_hours

    def _get_next_delivery_date(self):
        self.ensure_one()
        availability_date = self._get_next_availability_date()
        context = {"purchase_lead_hour__availability_date": availability_date}
        delay = self.with_context(context)._get_delay_delta()
        return availability_date + delay
