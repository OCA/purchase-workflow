# Copyright 2024 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestStockRule(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplierinfo_obj = cls.env["product.supplierinfo"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Mrs. Odoo 2"})
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.partner2.id,
                            "purchase_partner_id": cls.partner.id,
                            "price": 100,
                        }
                    )
                ],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.partner2.id,
                            "price": 50,
                        }
                    )
                ],
            }
        )

    def _create_orderpoint(self, product):
        return self.env["stock.warehouse.orderpoint"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_min_qty": 1,
                "product_max_qty": 10,
                "trigger": "manual",
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_replenishment_with_vendor_purchase(self):
        op = self._create_orderpoint(self.product1)
        op.action_replenish()
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.partner.id)], order="id desc", limit=1
        )
        self.assertEqual(purchase.partner_id, self.partner)
        self.assertEqual(purchase.order_line.product_id, self.product1)
        self.assertEqual(purchase.order_line.price_unit, 100)
        self.assertEqual(purchase.order_line.product_qty, 10)

    @mute_logger("odoo.models.unlink")
    def test_replenishment_without_vendor_purchase(self):
        op = self._create_orderpoint(self.product2)
        op.action_replenish()
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.partner2.id)], order="id desc", limit=1
        )
        self.assertEqual(purchase.partner_id, self.partner2)
        self.assertEqual(purchase.order_line.product_id, self.product2)
        self.assertEqual(purchase.order_line.price_unit, 50)
        self.assertEqual(purchase.order_line.product_qty, 10)
