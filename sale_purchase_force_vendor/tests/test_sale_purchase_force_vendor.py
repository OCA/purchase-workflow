# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

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

    def _create_service_order(self, vendors):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.service.id, "vendor_id": vendor.id}
                    )
                    for vendor in vendors
                ],
            }
        )

    def test_service_forced_vendor(self):
        order = self._create_service_order([self.vendor_b])
        order.action_confirm()
        purchase = order._get_purchase_orders()
        self.assertEqual(purchase.partner_id, self.vendor_b)
        self.assertEqual(purchase.order_line.price_unit, 20)

    def test_service_no_forced_vendor(self):
        order = self._create_service_order([self.env["res.partner"]])
        order.action_confirm()
        self.assertEqual(order._get_purchase_orders().partner_id, self.vendor_a)

    def test_service_lines_split_by_vendor(self):
        order = self._create_service_order([self.vendor_b, self.env["res.partner"]])
        order.action_confirm()
        purchases = order._get_purchase_orders()
        self.assertEqual(len(purchases), 2)
        self.assertEqual(purchases.partner_id, self.vendor_a | self.vendor_b)

    def test_service_vendor_without_supplierinfo(self):
        vendor_c = self.env["res.partner"].create({"name": "Test vendor C"})
        self.env.company.sale_purchase_force_vendor_restrict = False
        order = self._create_service_order([vendor_c])
        order.action_confirm()
        self.assertEqual(order._get_purchase_orders().partner_id, vendor_c)
        self.assertIn(vendor_c, self.service.seller_ids.partner_id)
