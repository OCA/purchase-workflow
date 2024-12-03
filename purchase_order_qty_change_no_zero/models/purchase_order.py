# Copyright 2024 Akretion - Clément Mombereau
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# from pprint import pprint

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_qty", "product_uom", "company_id")
    def _onchange_quantity(self):
        original_price_unit = self.price_unit
        super()._onchange_quantity()
        if original_price_unit and not self.price_unit:
            self.price_unit = original_price_unit
