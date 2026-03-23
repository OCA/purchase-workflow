# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_etd = fields.Date(string="ETD", help="Estimated Time of Departure")
    date_eta = fields.Date(string="ETA", help="Estimated Time of Arrival")
    shipping_schedule_note = fields.Char(
        help="Additional shipping schedule instructions or clarifications. "
        "Use this field when ETD or ETA cannot be expressed as a specific date "
        "(for example: ASAP, TBD, etc.).",
    )

    def display_expected_arrival(self):
        self.ensure_one()
        if (
            self.company_id.hide_expected_arrival_when_eta and self.date_eta
        ) or not self.date_planned:
            return False
        return True
