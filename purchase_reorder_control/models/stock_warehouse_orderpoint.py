# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_orderpoint_products(self):
        """Override to exclude unpurchaseable products"""
        products = super()._get_orderpoint_products()
        return products.filtered(lambda p: p.purchase_ok)

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        for rule in rules:
            if not rule.product_id.purchase_ok:
                raise UserError(_("Unpurchaseable Products cannot be reordered"))
        return rules
