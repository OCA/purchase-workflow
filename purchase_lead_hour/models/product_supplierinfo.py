# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # In odoo core, this field is an Integer, which in some cases,
    # could not be accurate enough.
    delay = fields.Float()

    def _get_next_availability_date(self):
        # A hook to ease overrides
        return fields.Datetime.now()
