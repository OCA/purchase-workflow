# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSalePurchaseForceVendorService(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.vendor_a = cls.env["res.partner"].create({"name": "Test vendor A"})
        cls.vendor_b = cls.env["res.partner"].create({"name": "Test vendor B"})
        cls.vendor_c = cls.env["res.partner"].create({"name": "Test vendor C"})
        cls.service = cls.env["product.product"].create(
            {
                "name": "Test subcontracted service",
                "type": "service",
                "service_to_purchase": True,
                "seller_ids": [
                    Command.create(
                        {"partner_id": cls.vendor_a.id, "min_qty": 1, "price": 10}
                    ),
                    Command.create(
                        {"partner_id": cls.vendor_b.id, "min_qty": 1, "price": 20}
                    ),
                ],
            }
        )

    def _create_sale_order(self, vendors):
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

    def test_forced_vendor(self):
        order = self._create_sale_order([self.vendor_b])
        order.action_confirm()
        purchase = order._get_purchase_orders()
        self.assertEqual(purchase.partner_id, self.vendor_b)
        self.assertEqual(purchase.order_line.price_unit, 20)

    def test_no_forced_vendor(self):
        order = self._create_sale_order([self.env["res.partner"]])
        order.action_confirm()
        self.assertEqual(order._get_purchase_orders().partner_id, self.vendor_a)

    def test_lines_split_by_vendor(self):
        order = self._create_sale_order([self.vendor_b, self.env["res.partner"]])
        order.action_confirm()
        purchases = order._get_purchase_orders()
        self.assertEqual(len(purchases), 2)
        self.assertEqual(purchases.partner_id, self.vendor_a | self.vendor_b)

    def test_vendor_without_supplierinfo(self):
        self.env.company.sale_purchase_force_vendor_restrict = False
        order = self._create_sale_order([self.vendor_c])
        order.action_confirm()
        self.assertEqual(order._get_purchase_orders().partner_id, self.vendor_c)
        self.assertIn(self.vendor_c, self.service.seller_ids.partner_id)
