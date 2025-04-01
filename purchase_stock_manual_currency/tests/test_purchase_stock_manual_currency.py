# Copyright 2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase


class TestPurchaseStockManualCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.currency_model = cls.env["res.currency"]
        cls.currency_rate_model = cls.env["res.currency.rate"]
        cls.stock_quant_model = cls.env["stock.quant"]
        cls.company_model = cls.env["res.company"]

        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.company = cls.company_model.create(
            {"name": "Test Company", "currency_id": cls.eur_currency.id}
        )

        cls.env.company = cls.company
        cls.partner = cls.partner_model.create({"name": "Test Partner"})

        cls.conv_rate = cls.currency_rate_model.create(
            {
                "name": "2024-08-30",
                "currency_id": cls.usd_currency.id,
                "rate": 1.11,
            }
        )

        cls.product_category = cls.product_category_model.create(
            {
                "name": "Average",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "categ_id": cls.product_category.id,
            }
        )
        cls.quants = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 100.0,
            }
        )

        cls.p_order = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner.id,
                "currency_id": cls.usd_currency.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_qty": 10.0,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 8.0,
                        },
                    ),
                ],
            }
        )

    def test_01_purchase_stock_manual_currency(self):
        self.p_order.manual_currency = False
        self.assertEqual(round(self.p_order.order_line.price_unit, 2), 8.0)
        self.assertEqual(round(self.p_order.order_line.price_subtotal, 2), 80.0)
        self.assertEqual(
            round(self.p_order.order_line.subtotal_company_currency, 2), 72.07
        )
        self.assertEqual(round(self.p_order.amount_untaxed, 2), 80.00)

        self.p_order.button_confirm()
        self.assertTrue(self.p_order.picking_ids)
        self.assertEqual(len(self.p_order.picking_ids), 1)
        stock_picking = self.p_order.picking_ids

        self.assertTrue(stock_picking.move_ids)
        self.assertEqual(len(stock_picking.move_ids), 1)
        stock_move = stock_picking.move_ids
        price = stock_move._get_price_unit()
        self.assertEqual(round(price, 2), 7.21)
        stock_picking.move_ids.write({"quantity": 10})
        stock_picking.button_validate()

        self.assertTrue(stock_move.stock_valuation_layer_ids)
        self.assertEqual(len(stock_move.stock_valuation_layer_ids), 1)
        svl = stock_move.stock_valuation_layer_ids
        self.assertEqual(svl.quantity, 10.0)
        self.assertEqual(round(svl.unit_cost, 2), 7.21)
        self.assertEqual(round(svl.value, 2), 72.07)

    def test_02_purchase_stock_manual_currency(self):
        self.p_order.manual_currency = True
        self.p_order.manual_currency_rate = 2.0
        self.p_order.type_currency = "company_rate"
        self.assertEqual(round(self.p_order.order_line.price_unit, 2), 8.0)
        self.assertEqual(round(self.p_order.order_line.price_subtotal, 2), 80.0)
        self.assertEqual(
            round(self.p_order.order_line.subtotal_company_currency, 2), 40.0
        )
        self.assertEqual(round(self.p_order.amount_untaxed, 2), 80.00)

        self.p_order.button_confirm()
        self.assertTrue(self.p_order.picking_ids)
        self.assertEqual(len(self.p_order.picking_ids), 1)
        stock_picking = self.p_order.picking_ids

        self.assertTrue(stock_picking.move_ids)
        self.assertEqual(len(stock_picking.move_ids), 1)
        stock_move = stock_picking.move_ids
        price = stock_move._get_price_unit()
        self.assertEqual(round(price, 2), 4.00)
        stock_picking.move_ids.write({"quantity": 10})
        stock_picking.button_validate()

        self.assertTrue(stock_move.stock_valuation_layer_ids)
        self.assertEqual(len(stock_move.stock_valuation_layer_ids), 1)
        svl = stock_move.stock_valuation_layer_ids
        self.assertEqual(svl.quantity, 10.0)
        self.assertEqual(round(svl.unit_cost, 2), 4.00)
        self.assertEqual(round(svl.value, 2), 40.00)

    def test_03_purchase_stock_manual_currency(self):
        self.p_order.currency_id = self.eur_currency
        self.p_order._onchange_currency_change_rate()
        self.assertEqual(round(self.p_order.order_line.price_unit, 2), 8.0)
        self.assertEqual(round(self.p_order.order_line.price_subtotal, 2), 80.0)
        self.assertEqual(
            round(self.p_order.order_line.subtotal_company_currency, 2), 80.0
        )
        self.assertEqual(round(self.p_order.amount_untaxed, 2), 80.00)

        self.p_order.button_confirm()
        self.assertTrue(self.p_order.picking_ids)
        self.assertEqual(len(self.p_order.picking_ids), 1)
        stock_picking = self.p_order.picking_ids

        self.assertTrue(stock_picking.move_ids)
        self.assertEqual(len(stock_picking.move_ids), 1)
        stock_move = stock_picking.move_ids
        price = stock_move._get_price_unit()
        self.assertEqual(round(price, 2), 8.00)
        stock_picking.move_ids.write({"quantity": 10})
        stock_picking.button_validate()

        self.assertTrue(stock_move.stock_valuation_layer_ids)
        self.assertEqual(len(stock_move.stock_valuation_layer_ids), 1)
        svl = stock_move.stock_valuation_layer_ids
        self.assertEqual(svl.quantity, 10.0)
        self.assertEqual(round(svl.unit_cost, 2), 8.00)
        self.assertEqual(round(svl.value, 2), 80.00)
