# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.purchase_order_product_recommendation.tests import test_recommendation


class RecommendationCase(test_recommendation.RecommendationCase):
    def test_export_wizard(self):
        """Recommendations are OK."""
        wizard = self.wizard()
        report_xlsx = self.env.ref(
            "purchase_order_product_recommendation_xlsx.recommendation_xlsx"
        )._render(wizard.ids)
        self.assertGreaterEqual(len(report_xlsx[0]), 1)
        self.assertEqual(report_xlsx[1], "xlsx")
