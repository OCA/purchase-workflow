# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.purchase_order_product_recommendation.tests import test_recommendation


class TestSaleProductClassification(test_recommendation.RecommendationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Quickly generate 3 products with a different price each. We'll be
        # using a new set of products to avoid history pollution.
        cls.forecasted_products = cls.env["product.product"].create(
            [
                {
                    "name": "Test product forecast {}".format(i + 4),
                    "type": "product",
                    "seller_ids": [(0, 0, {"name": cls.partner.id})],
                }
                for i in range(3)
            ]
        )
        cls.prod_4, cls.prod_5, cls.prod_6 = cls.forecasted_products
        # History of deliveries we want to reproduce separeted for the periods
        # we'll evaluate.
        # - Period X is the one we set in the wizard
        # - Period A and B are those computed from the year of reference
        # Let's create the move lines according to this history
        history_data = {
            # Period A (p4, p5, p6)
            "2019-03-05": (5, 18, 520),
            "2019-03-10": (6, 1, 436),
            "2019-03-20": (6, 0, 654),
            # Period B next(A) (p4, p5, p6)
            "2019-04-05": (18, 0, 40),
            "2019-04-10": (20, 0, 65),
            "2019-04-20": (15, 19, 68),
            # Period X (p4, p5, p6)
            "2021-03-05": (3, 10, 215),
            "2021-03-10": (2, 0, 158),
            "2021-03-20": (5, 2, 120),
        }
        cls.sml_forecast = cls.env["stock.move.line"]
        for history_date, history_tuple in history_data.items():
            history_date = fields.Datetime.from_string(history_date)
            cls.sml_forecast |= cls.env["stock.move.line"].create(
                [
                    {
                        "date": history_date,
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "qty_done": qty,
                        "location_id": cls.wh1.lot_stock_id.id,
                        "location_dest_id": cls.customer_loc.id,
                        "company_id": cls.env.company.id,
                    }
                    for product, qty in zip(cls.forecasted_products, history_tuple)
                    if qty
                ]
            )
        # Ensure that the state is set
        cls.sml_forecast.write({"state": "done"})
        # Initializa current stock:
        #  p4 | p5 | p6
        #  15 | 10 | 200
        cls.env["stock.quant"].create(
            [
                {
                    "product_id": product.id,
                    "location_id": cls.wh1.lot_stock_id.id,
                    "quantity": qty,
                }
                for product, qty in zip(cls.forecasted_products, (15, 10, 200))
            ]
        )

    def test_recommendation_forecast(self):
        """Test forecast for different products and slices of time"""
        # We'll be choosing period X for the wizard
        wizard = self.wizard()
        wizard.date_begin = "2021-03-01"
        wizard.date_end = "2021-03-31"
        wizard.year_of_reference = "2019"
        wizard._generate_recommendations()
        # The table of truth for the increments should be:
        #    p4    |  p5   |   p6
        # ---------|-------|---------
        #  211,76% | 0,00% | -89,25%
        line_p4 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.forecasted_products[0]
        )
        line_p5 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.forecasted_products[1]
        )
        line_p6 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.forecasted_products[2]
        )
        self.assertAlmostEqual(line_p4.forecasted_increment, 2.1176, 4)
        self.assertAlmostEqual(line_p5.forecasted_increment, 0)
        self.assertAlmostEqual(line_p6.forecasted_increment, -0.8925, 4)
        # The table of truth for the reccomended quantities according to the
        # current stock should be this:
        # p  | rec |    %    | fcst  | rec %
        # p4 |   0 | 211,76% | 31,18 | 16,18 -> expected increment
        # p5 |   2 |   0,00% |    12 |     2 -> no change expected
        # p6 | 293 | -89,25% | 52,97 |     0 -> sales will drop; don't ressuply
        # rec: normal recommendation
        # fcst: units that we expect to deliver
        # rec %: recommendation according to forecast and current stock
        self.assertAlmostEqual(line_p4.units_forecasted, 31.18, 2)
        self.assertAlmostEqual(line_p4.units_included, 16.18, 2)
        self.assertAlmostEqual(line_p5.units_forecasted, 12)
        self.assertAlmostEqual(line_p5.units_included, 2)
        self.assertAlmostEqual(line_p6.units_forecasted, 52.97, 2)
        self.assertAlmostEqual(line_p6.units_included, 0)
