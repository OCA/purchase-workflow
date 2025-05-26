# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSalePurchaseForceVendorBase


class TestSalePurchaseForceVendor(TestSalePurchaseForceVendorBase):
    def test_misc(self):
        self.sale_order.action_confirm()
        purchase_orders = self.sale_order._get_purchase_orders()
        self.assertEqual(len(purchase_orders), 1)
        self.assertEqual(purchase_orders.partner_id, self.vendor_b)
        self.assertEqual(len(self.product_a.seller_ids), 2)
        self.assertNotIn(self.vendor_a, self.product_b.seller_ids.mapped("partner_id"))
        self.assertIn(self.vendor_b, self.product_b.seller_ids.mapped("partner_id"))

    def test_misc_force_vendor_restrict(self):
        self.env.company.sale_purchase_force_vendor_restrict = True
        self.sale_order.action_confirm()
        partners_sol_a = self.env["res.partner"].search(self.sol_a.vendor_id_domain)
        self.assertNotIn(self.partner, partners_sol_a)
        self.assertIn(self.vendor_a, partners_sol_a)
        self.assertIn(self.vendor_b, partners_sol_a)
        partners_sol_b = self.env["res.partner"].search(self.sol_b.vendor_id_domain)
        self.assertNotIn(self.partner, partners_sol_b)
        self.assertNotIn(self.vendor_a, partners_sol_b)
        self.assertIn(self.vendor_b, partners_sol_b)

    def test_misc_not_force_vendor_restrict(self):
        self.env.company.sale_purchase_force_vendor_restrict = False
        self.sale_order.action_confirm()
        self.assertEqual(self.sol_a.vendor_id_domain, [])
        self.assertEqual(self.sol_b.vendor_id_domain, [])
