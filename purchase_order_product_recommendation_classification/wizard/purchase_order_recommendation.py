# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    sale_classification = fields.Selection(
        selection=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D"),],
        string="Sales classification",
    )
    seasonality_classification = fields.Selection(
        selection=[
            ("very high", "Very high"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        string="Seasonility",
    )

    def _get_products(self):
        """Filter products of the given classifications"""
        products = super()._get_products()
        if self.sale_classification:
            products = products.filtered(
                lambda x: x.sale_classification == self.sale_classification
            )
        if self.seasonality_classification:
            products = products.filtered(
                lambda x: (
                    x.seasonality_classification == self.seasonality_classification
                )
            )
        return products

    def _get_all_products_domain(self):
        """Filter products of the given classifications"""
        domain = super()._get_all_products_domain()
        if self.sale_classification:
            domain += [("sale_classification", "=", self.sale_classification)]
        if self.seasonality_classification:
            domain += [
                ("seasonality_classification", "=", self.seasonality_classification)
            ]
        return domain

    @api.onchange("sale_classification", "seasonality_classification")
    def _generate_classification_recommendations(self):
        """Trigger the general onchange method"""
        return super()._generate_recommendations()


class PurchaseOrderRecommendationLine(models.TransientModel):
    _inherit = "purchase.order.recommendation.line"

    sale_classification = fields.Selection(
        related="product_id.sale_classification", readonly=True,
    )
    seasonality_classification = fields.Selection(
        related="product_id.seasonality_classification", readonly=True,
    )
