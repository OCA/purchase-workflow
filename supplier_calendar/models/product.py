# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    delay_calendar_type = fields.Selection(
        related="partner_id.delay_calendar_type", readonly=True
    )

    def _get_natural_delay(self, company):
        """The lead time counted in the working days of the supplier calendar,
        as natural days from today."""
        self.ensure_one()
        calendar = self.delay and self.partner_id._get_supplier_calendar(company)
        if not calendar:
            return self.delay
        today = fields.Date.today()
        key = ("supplier_calendar_lead_days", calendar.id, today, self.delay)
        if key not in self.env.cr.cache:
            date_receipt = self.partner_id.supplier_plan_days(
                today, self.delay, company
            )
            self.env.cr.cache[key] = (
                (date_receipt.date() - today).days if date_receipt else self.delay
            )
        return self.env.cr.cache[key]

    def _with_natural_delay(self, company):
        """In-memory copy of the vendor line with its natural lead time."""
        self.ensure_one()
        delay = self._get_natural_delay(company)
        if delay == self.delay:
            return self
        return self.new({"delay": delay}, origin=self._origin)
