# Copyright 2021 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.purchase_order_product_recommendation.tests import test_recommendation


class ClassificationRecommendationCase(test_recommendation.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = cls.env["abc.classification.profile"].create(
            {
                "name": "Test Profile",
                "classification_type": "fixed",
                "data_source": "sale_report",
                "value_criteria": "sold_delivered_value",
            }
        )
        cls.a = cls.env["abc.classification.profile.level"].create(
            {"profile_id": cls.profile.id, "fixed": 10000}
        )
        cls.b = cls.env["abc.classification.profile.level"].create(
            {"profile_id": cls.profile.id, "fixed": 5000}
        )
        cls.prod_1.abc_classification_profile_id = cls.profile
        cls.prod_2.abc_classification_profile_id = cls.profile
        cls.prod_3.abc_classification_profile_id = cls.profile
        cls.prod_1.abc_classification_level_id = cls.a
        cls.prod_2.abc_classification_level_id = cls.b
        cls.prod_3.abc_classification_level_id = cls.b
        cls.prod_1.seasonality_classification = "high"
        cls.prod_2.seasonality_classification = "high"
        cls.prod_3.seasonality_classification = "low"

    def test_recommendations_by_classification(self):
        """We can filter by brand"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = "2019-02-01"
        # Just delivered from brand 1
        wizard.abc_classification_profile_id = self.profile
        wizard.abc_classification_level_id = self.b
        wizard.seasonality_classification = "high"
        wizard.show_all_partner_products = True
        wizard._generate_recommendations()
        # Just one line with products from brand 1
        self.assertEqual(wizard.line_ids.product_id, self.prod_2)
