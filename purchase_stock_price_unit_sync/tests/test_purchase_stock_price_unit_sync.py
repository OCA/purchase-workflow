# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import SavepointCase


class TestProductCostPriceAvcoSync(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Category property_cost_method average",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "type": "product",
                "tracking": "none",
                "categ_id": cls.product_category.id,
                "standard_price": 1,
            }
        )

        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_qty": 10.0,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": fields.Date.today(),
                            "price_unit": 8.0,
                        },
                    ),
                ],
            }
        )

    def test_sync_cost_price(self):
        self.order.button_confirm()
        picking = self.order.picking_ids[:1]
        move = picking.move_lines[:1]
        move.quantity_done = move.product_uom_qty
        picking._action_done()
        self.assertAlmostEqual(move.stock_valuation_layer_ids[:1].unit_cost, 8.0, 2)
        self.order.order_line[:1].price_unit = 6.0
        self.assertAlmostEqual(move.stock_valuation_layer_ids[:1].unit_cost, 6.0, 2)
