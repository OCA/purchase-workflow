# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestPurchaseOrderLineInitialQuantity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Purchase Orders ====
        cls.order1 = cls.env.ref("purchase.purchase_order_1")
        cls.order1.button_confirm()
        # ==== Purchase Order Lines====
        cls.line = cls.order1.order_line[0]

    def test_update_purchase_order_line_qty(self):
        self.assertFalse(self.order1.initial_qty_changed)
        self.assertEqual(self.line.product_qty, self.line.product_initial_qty)
        # change the product quantity
        self.line.write({"product_qty": 9.0})
        self.assertEqual(self.line.product_initial_qty, 15.0)
        self.assertTrue(self.order1.initial_qty_changed)
