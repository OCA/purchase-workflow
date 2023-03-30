# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    purchase_lines_count = fields.Integer(
        compute="_compute_purchase_lines_count", string="Purchased products"
    )

    def _compute_purchase_lines_count(self):
        if not self.user_has_groups("purchase.group_purchase_user") or not self.ids:
            self.purchase_lines_count = 0.0
            return
        domain = [
            ("state", "in", ["purchase", "done"]),
            ("product_id", "in", self.ids),
            ("company_id", "in", self.env.companies.ids),
        ]
        purchase_line_data = self.env["purchase.order.line"].read_group(
            domain, ["product_id"], ["product_id"]
        )
        mapped_data = {
            m["product_id"][0]: m["product_id_count"] for m in purchase_line_data
        }
        for product in self:
            product.purchase_lines_count = mapped_data.get(product.id, 0)
