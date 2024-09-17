# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockMovePurchasePriceUpdate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Partner Test",
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 3,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.00,
                        },
                    ),
                ],
            }
        )
        cls.purchase_order.onchange_partner_id()
        cls.purchase_order_line = cls.purchase_order.order_line[0]
        cls.purchase_order.button_confirm()
        cls.picking = cls.purchase_order.picking_ids

    def test_stock_move_purchase_price(self):
        moves = self.picking.move_lines
        self.assertEqual(moves[0].purchase_price_unit, 100.0)
        moves[0].write({"purchase_price_unit": 123.0})
        self.assertEqual(self.purchase_order_line.price_unit, 123.0)

    def test_stock_move_line_purchase_price(self):
        move_lines = self.picking.move_line_ids
        self.assertEqual(move_lines[0].purchase_price_unit, 100.0)
        move_lines[0].write({"purchase_price_unit": 123.0})
        self.assertEqual(self.purchase_order_line.price_unit, 123.0)
