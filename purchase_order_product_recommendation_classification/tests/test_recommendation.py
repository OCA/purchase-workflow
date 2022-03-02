# Copyright 2021 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.purchase_order_product_recommendation.tests import test_recommendation


class ClassificationRecommendationCase(test_recommendation.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prod_1.sale_classification = "a"
        cls.prod_2.sale_classification = "b"
        cls.prod_3.sale_classification = "b"
        cls.prod_1.seasonality_classification = "high"
        cls.prod_2.seasonality_classification = "high"
        cls.prod_3.seasonality_classification = "low"

    def test_recommendations_by_classification(self):
        """We can filter by brand"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = "2019-02-01"
        # Just delivered from brand 1
        wizard.sale_classification = "b"
        wizard.seasonality_classification = "high"
        wizard.show_all_partner_products = True
        wizard._generate_recommendations()
        # Just one line with products from brand 1
        self.assertEqual(wizard.line_ids.product_id, self.prod_2)
