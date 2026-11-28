# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def _cron_recompute_main_seller_id(self):
        products = self.env["product.product"].search([])
        templates = self.env["product.template"].search([])
        products._compute_main_seller_id()
        templates._compute_main_seller_id()
