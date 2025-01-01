# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.addons.base.tests.common import BaseCommon


class TestPurchase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product", "detailed_type": "product"}
        )
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "name": cls.product.name,
                            "price_unit": cls.product.standard_price,
                            "date_planned": date.today(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.purchase_line = cls.purchase.order_line[0]
        cls._create_stock_move(10.0)

    @classmethod
    def _create_stock_move(cls, qty):
        stock_move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "location_id": cls.location_suppliers.id,
                "location_dest_id": cls.location_stock.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": qty,
            }
        )
        stock_move._action_done()

    def test_purchase_line_virtual_available(self):
        self.assertEqual(self.purchase_line.virtual_available, 10.0)
        self._create_stock_move(20.0)
        self.assertEqual(self.purchase_line.virtual_available, 30.0)
