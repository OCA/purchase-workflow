# Copyright 2025 Juan Alberto Raja<juan.raja@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _add_supplier_to_product(self):
        result = None
        if self.company_id.purchase_pricelist_disable_autocreate:
            result = super()._add_supplier_to_product()
        return result
