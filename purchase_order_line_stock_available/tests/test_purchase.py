# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests import common


class TestPurchase(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.product = self.env["product.product"].create(
            {"name": "Test product", "detailed_type": "product"}
        )
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.location_suppliers = self.env.ref("stock.stock_location_suppliers")
        self.purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "name": self.product.name,
                            "price_unit": self.product.standard_price,
                            "date_planned": date.today(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        self.purchase_line = self.purchase.order_line[0]
        self._create_stock_move(10.0)

    def _create_stock_move(self, qty):
        stock_move = self.env["stock.move"].create(
            {
                "name": self.product.display_name,
                "location_id": self.location_suppliers.id,
                "location_dest_id": self.location_stock.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": qty,
            }
        )
        stock_move._action_done()

    def test_purchase_line_virtual_available(self):
        self.assertEqual(self.purchase_line.virtual_available, 10.0)
        self._create_stock_move(20.0)
        self.assertEqual(self.purchase_line.virtual_available, 30.0)
