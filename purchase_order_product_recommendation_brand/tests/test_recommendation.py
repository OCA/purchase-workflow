# Copyright 2019 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.purchase_order_product_recommendation.tests import test_recommendation


class BrandRecommendationCase(test_recommendation.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand_obj = cls.env["product.brand"]
        cls.brand_1 = cls.brand_obj.create({"name": "OCA Cola"})
        cls.brand_2 = cls.brand_obj.create({"name": "Play-Odoo"})
        cls.prod_1.product_brand_id = cls.brand_1
        cls.prod_2.product_brand_id = cls.brand_2
        cls.prod_3.product_brand_id = cls.brand_2

    def test_recommendations_by_brand(self):
        """We can filter by brand"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = "2019-02-01"
        # Just delivered from brand 1
        wizard.product_brand_ids = self.brand_1
        wizard.show_all_partner_products = True
        wizard._generate_recommendations()
        # Just one line with products from brand 1
        self.assertEqual(wizard.line_ids.product_id, self.prod_1)
        # Just delivered from brand 2
        wizard.product_brand_ids = self.brand_2
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)
        # All brands
        wizard.product_brand_ids += self.brand_1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 3)
        # No brand set
        wizard.product_brand_ids = False
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 3)

    def test_recommendations_by_brand_all_products(self):
        """Brand filters also apply to all products filter"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = "2019-02-01"
        # First we show all purchasable products
        wizard.show_all_products = True
        wizard.line_amount = 0
        wizard._generate_recommendations()
        purchase_products_number = self.product_obj.search_count(
            [("purchase_ok", "!=", False)]
        )
        self.assertEqual(len(wizard.line_ids), purchase_products_number)
        # Then we filter by brand
        wizard.product_brand_ids = self.brand_2
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)
