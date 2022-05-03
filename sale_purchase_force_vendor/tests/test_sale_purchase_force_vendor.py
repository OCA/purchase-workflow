# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSalePurchaseForceVendorBase


class TestSalePurchaseForceVendor(TestSalePurchaseForceVendorBase):
    def test_misc(self):
        self.sale_order.action_confirm()
        self.assertNotIn(self.partner, self.sale_order.order_line.allowed_vendor_ids)
        self.assertIn(self.vendor_a, self.sale_order.order_line.allowed_vendor_ids)
        self.assertIn(self.vendor_b, self.sale_order.order_line.allowed_vendor_ids)
        purchase_orders = self.sale_order._get_purchase_orders()
        self.assertEqual(len(purchase_orders), 1)
        self.assertEqual(purchase_orders.partner_id, self.vendor_b)
        self.assertEqual(len(self.product_a.seller_ids), 2)
        self.assertNotIn(self.vendor_a, self.product_b.seller_ids.mapped("name"))
        self.assertIn(self.vendor_b, self.product_b.seller_ids.mapped("name"))
