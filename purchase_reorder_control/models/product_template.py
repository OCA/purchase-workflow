# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_ok = fields.Boolean(tracking=True)

    def write(self, vals):
        """
        Remove reordering rules associated with products when purchase_ok = False
        """
        res = super().write(vals)
        if "purchase_ok" in vals and not vals.get("purchase_ok"):
            orderPointObject = self.env["stock.warehouse.orderpoint"]
            rules = orderPointObject.search(
                [("product_id", "in", self.mapped("product_variant_ids").ids)]
            )
            orderPointObject.browse(rules.ids).unlink()
        return res
