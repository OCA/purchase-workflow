# Copyright 2019 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    allowed_brand_domain = fields.Binary(compute="_compute_allowed_brand_domain")
    product_brand_ids = fields.Many2many(comodel_name="product.brand", string="Brands")

    def _get_products(self):
        """Filter products of the given brands"""
        products = super()._get_products()
        # Filter products by brand if set.
        # It will apply to show_all_partner_products as well
        if self.product_brand_ids:
            # We are in onchange context, so to avoid to compare records with
            # new_id instances we use self.product_brand_ids.ids,
            # self.product_brand_ids = newid but self.product_brand_ids.ids is a real id
            products = products.filtered(
                lambda x: x.product_brand_id.id in self.product_brand_ids.ids
            )
        return products

    def _get_all_products_domain(self):
        """Filter products of the given brands"""
        domain = super()._get_all_products_domain()
        if self.product_brand_ids and not self.env.context.get("no_brands_filter"):
            domain += [("product_brand_id", "in", self.product_brand_ids.ids)]
        return domain

    @api.depends("show_all_partner_products", "show_all_products")
    def _compute_allowed_brand_domain(self):
        """Restrict available brands domain"""
        for record in self:
            products = record._get_supplier_products()
            # Gets all products avoiding to filter them by brand again
            if record.show_all_products:
                products += (
                    record.with_context(no_brands_filter=True)
                    .env["product.product"]
                    .search(record._get_all_products_domain())
                )
            brands = products.mapped("product_brand_id")
            record.allowed_brand_domain = [("id", "in", brands.ids)]

    @api.onchange(
        "order_id",
        "date_begin",
        "date_end",
        "line_amount",
        "show_all_partner_products",
        "show_all_products",
        "product_category_ids",
        "warehouse_ids",
        "product_brand_ids",
    )
    def _generate_recommendations(self):
        """Just to add field to the onchange method"""
        return super()._generate_recommendations()
