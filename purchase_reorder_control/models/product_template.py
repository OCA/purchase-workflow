# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_ok = fields.Boolean(tracking=True)

    def write(self, vals):
        """
        Archive reordering rules associated with products when purchase_ok = False
        """
        res = super().write(vals)
        if "purchase_ok" in vals:
            orderPointObject = self.env["stock.warehouse.orderpoint"]
            rules = orderPointObject.with_context(active_test=False).search(
                [("product_id", "in", self.mapped("product_variant_ids").ids)]
            )
            orderPointObject.browse(rules.ids).write(
                {"active": vals.get("purchase_ok", False)}
            )
        return res
