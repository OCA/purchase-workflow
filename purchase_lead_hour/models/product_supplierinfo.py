# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # In odoo core, we can only set an amount of days,
    # which could not be accurate enough.
    delay_hour = fields.Integer("Delivery Lead Time Hour")

    def _get_next_availability_date(self):
        # A hook to ease overrides
        return fields.Datetime.now()
