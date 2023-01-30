# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestPurchaseOrderLineQtyToReceive(TransactionCase):
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
        cls.order_line = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.order.id,
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_qty": 10.0,
            }
        )

    def test_00_nothing_received(self):
        self.order.order_line.qty_received_manual = 0
        self.assertEqual(self.order_line.qty_to_receive, 10)

    def test_01_partially_received(self):
        self.order.order_line.qty_received_manual = 3
        self.assertEqual(self.order_line.qty_to_receive, 7)

    def test_02_totally_received(self):
        self.order.order_line.qty_received_manual = 10
        self.assertEqual(self.order_line.qty_to_receive, 0)
