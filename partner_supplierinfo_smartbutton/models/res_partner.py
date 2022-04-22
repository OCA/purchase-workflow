# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    product_supplied_count = fields.Integer(
        compute="_compute_product_supplied_count", string="Product Supplied Count"
    )

    def _compute_product_supplied_count(self):
        supplierinfo_data = self.env["product.supplierinfo"].read_group(
            [("name", "in", self.ids)], ["name"], ["name"]
        )
        mapping = {data["name"][0]: data["name_count"] for data in supplierinfo_data}
        for item in self:
            item.product_supplied_count = mapping.get(item.id, 0)

    def action_see_products_by_seller(self):
        domain = [("name", "=", self.id)]
        res = self.env.ref("product.product_supplierinfo_type_action").sudo().read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_name": self.id,
                "search_default_name": self.id,
                "visible_product_tmpl_id": False,
            }
        )
        res.update({"domain": domain, "context": ctx})
        return res
