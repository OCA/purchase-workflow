# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseOrderLine(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_id = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "detailed_type": "consu",
            }
        )

        cls.partner_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        cls.partner2_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
            }
        )

        cls.purchase_supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner_id.id,
                "product_tmpl_id": cls.product_id.product_tmpl_id.id,
                "price": 100.0,
            }
        )

        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_id.id,
            }
        )

    def test_update_supplierinfo_price(self):

        purchase_order_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product_id.id,
                "product_qty": 1.0,
                "price_unit": 120.0,
            }
        )

        purchase_order_line.action_update_product_supplierinfo()

        self.assertEqual(
            self.purchase_supplierinfo.price,
            120.0,
            "The supplier info price should be updated to the purchase order line price.",
        )

    def test_create_non_existing_supplierinfo(self):
        self.purchase_order.partner_id = self.partner2_id.id

        purchase_order_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product_id.id,
                "product_qty": 1.0,
                "price_unit": 150.0,
            }
        )

        purchase_order_line.action_update_product_supplierinfo()

        new_supplierinfo = self.env["product.supplierinfo"].search(
            [
                ("partner_id", "=", self.partner2_id.id),
                ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
            ],
            limit=1,
        )

        self.assertTrue(
            new_supplierinfo, "A new supplier info should be created for the partner."
        )

        self.assertEqual(
            new_supplierinfo.price,
            150.0,
            "The new supplier info price should match the purchase order line price.",
        )

    def test_can_update_product_supplierinfo(self):
        purchase_order_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product_id.id,
                "product_qty": 1.0,
                "price_unit": 120.0,
            }
        )

        # Check if can_update_price is True initially
        self.assertTrue(
            purchase_order_line.can_update_product_supplierinfo,
            "can_update_product_supplierinfo should be True before action.",
        )

        purchase_order_line.action_update_product_supplierinfo()

        # After updating, can_update_price should be False
        purchase_order_line.invalidate_recordset()
        self.assertFalse(
            purchase_order_line.can_update_product_supplierinfo,
            "can_update_product_supplierinfo should be False after action.",
        )

        # If the supplier price is changed, can_update_price should be True again
        self.purchase_supplierinfo.price = 130.0
        purchase_order_line.invalidate_recordset()
        self.assertTrue(
            purchase_order_line.can_update_product_supplierinfo,
            "can_update_product_supplierinfo should be True after supplierinfo price change.",
        )
