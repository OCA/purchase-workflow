# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)
        if "active" in vals:
            self.env["product.supplierinfo"].search(
                [("product_tmpl_id", "in", self.ids)]
            ).write({"is_product_active": vals["active"]})
        return res
