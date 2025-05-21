# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestPurchaseReceiptionStatusLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Purchase Partner"})
        cls.product = cls.env["product.product"].create(
            # Use "service" type product to be able to set receipt qty manually
            {"name": "Purchase Product", "type": "service"}
        )
        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "company_id": cls.env.user.company_id.id,
            }
        )

    def test_01_order_empty_with_lines(self):
        """Test empty order w/ lines: receipt status should be received"""
        line1 = self.env["purchase.order.line"].create(
            {
                "order_id": self.order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 0.0,
            }
        )
        self.order.button_confirm()
        self.assertEqual(line1.reception_status, "received")

    def test_02_order_with_lines(self):
        """Test order w/ lines

        Add 2 lines:
            1) 20u ordered, 0u received
            2) 5u ordered, 5u received
        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.order.id,
                    "name": self.product.name,
                    "product_id": self.product.id,
                    "product_qty": 20.0,
                    "qty_received_manual": 0.0,
                },
                {
                    "order_id": self.order.id,
                    "name": self.product.name,
                    "product_id": self.product.id,
                    "product_qty": 5.0,
                    "qty_received_manual": 3.0,
                },
            ]
        )
        self.order.button_confirm()
        self.assertEqual(self.order.order_line[0].reception_status, "no")
        self.assertEqual(self.order.order_line[1].reception_status, "partial")
        self.order.order_line[0].force_received = True
        self.assertEqual(self.order.order_line[0].reception_status, "received")
        self.assertEqual(self.order.order_line[1].reception_status, "partial")
        self.order.order_line[1].force_received = True
        self.assertEqual(self.order.order_line[0].reception_status, "received")
        self.assertEqual(self.order.order_line[1].reception_status, "received")
        self.order.order_line[1].force_received = False
        self.assertEqual(self.order.order_line[0].reception_status, "received")
        self.assertEqual(self.order.order_line[1].reception_status, "partial")
        self.order.force_received = True
        self.assertEqual(self.order.order_line[0].reception_status, "received")
        self.assertEqual(self.order.order_line[1].reception_status, "received")
        self.assertEqual(self.order.order_line[1].force_received, True)

    def test_03_over_received_status(self):
        over_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 5.0,
                "qty_received_manual": 7.0,
            }
        )
        self.order.button_confirm()
        self.assertEqual(over_line.reception_status, "over")
        over_line.force_received = True
        self.assertEqual(over_line.reception_status, "received")

    def test_04_order_force_logic_and_propagation(self):
        l1 = self.env["purchase.order.line"].create(
            {
                "order_id": self.order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 4.0,
                "qty_received_manual": 0.0,
            }
        )
        l2 = self.env["purchase.order.line"].create(
            {
                "order_id": self.order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 3.0,
                "qty_received_manual": 0.0,
            }
        )
        self.order.button_confirm()
        self.assertTrue(l1.reception_status == "no")
        self.assertTrue(l2.reception_status == "no")
        self.assertFalse(self.order.force_received)
        l1.force_received = True
        self.assertFalse(self.order.force_received)
        l2.force_received = True
        self.assertTrue(self.order.force_received)
        l1.force_received = False
        self.assertFalse(self.order.force_received)
        self.assertTrue(l2.force_received)
        self.order.force_received = True
        self.assertTrue(all(line.force_received for line in self.order.order_line))
        self.order.force_received = False
        self.assertFalse(any(line.force_received for line in self.order.order_line))
