# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    delay = fields.Float()

    def get_next_availability_date(self):
        # A hook to ease overrides
        return fields.Datetime.now()
