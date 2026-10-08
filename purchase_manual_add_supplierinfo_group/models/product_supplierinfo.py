# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    def update_from_purchase(self, create=True):
        return super(
            ProductSupplierinfo, self.with_context(skip_group_specific=False)
        ).update_from_purchase(create=create)
