# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    abc_classification_profile_id = fields.Many2one(
        comodel_name="abc.classification.profile", string="Classification Profile",
    )
    abc_classification_level_id = fields.Many2one(
        comodel_name="abc.classification.profile.level",
        string="Classification Level",
        domain="[('profile_id', '=', abc_classification_profile_id)]",
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
        if self.abc_classification_profile_id and self.abc_classification_level_id:
            products = products.filtered(
                lambda x: x.abc_classification_profile_id
                == self.abc_classification_profile_id
                and x.abc_classification_level_id == self.abc_classification_level_id
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
        if self.abc_classification_profile_id and self.abc_classification_level_id:
            domain += [
                (
                    "abc_classification_profile_id",
                    "=",
                    self.abc_classification_profile_id.id,
                ),
                (
                    "abc_classification_level_id",
                    "=",
                    self.abc_classification_level_id.id,
                ),
            ]
        if self.seasonality_classification:
            domain += [
                ("seasonality_classification", "=", self.seasonality_classification)
            ]
        return domain

    @api.onchange(
        "abc_classification_profile_id",
        "abc_classification_level_id",
        "seasonality_classification",
    )
    def _generate_classification_recommendations(self):
        """Trigger the general onchange method"""
        return super()._generate_recommendations()


class PurchaseOrderRecommendationLine(models.TransientModel):
    _inherit = "purchase.order.recommendation.line"

    abc_classification_profile_id = fields.Many2one(
        comodel_name="abc.classification.profile",
        related="product_id.abc_classification_profile_id",
        readonly=True,
    )
    abc_classification_level_id = fields.Many2one(
        comodel_name="abc.classification.profile.level",
        related="product_id.abc_classification_level_id",
        readonly=True,
    )
    seasonality_classification = fields.Selection(
        related="product_id.seasonality_classification", readonly=True,
    )
