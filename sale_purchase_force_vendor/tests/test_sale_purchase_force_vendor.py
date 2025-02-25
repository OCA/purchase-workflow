# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_order_line_chained_move.tests.test_chained_move import (
    TestSaleChainedMove as TestSaleOrderLineChainedMoveBase,
)

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


class TestSalePurchaseForceVendorChainedMove(TestSaleOrderLineChainedMoveBase):
    """
    This class makes a test with another route than the default Odoo MTO route.
    It uses the route defined in sale_order_line_chained_move, which is a
    3-steps delivery: Pick/Pack/Ship.
    """

    def test_force_vendor_on_mto_like_route(self):
        """
        Test that the vendor is correctly forced on a PO even on a more
        complicated MTO-like route.
        We configure the rules of the route as following:
        Out -> Customer: pull; make_to_order
        Pack -> Out: pull; make_to_order
        Stock -> Pack: pull; make_to_order
        In Stock: buy route
        The 3 first rules are defined in sale_order_line_chained_move test class.
        We add the buy route in this test.
        """
        self.stock_out_rule.procure_method = "make_to_order"
        self.env["stock.rule"].create(
            {
                "name": "Buy",
                "route_id": self.route.id,
                "action": "buy",
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
            }
        )
        vendor_a = self.env["res.partner"].create({"name": "Test Vendor A"})
        vendor_b = self.env["res.partner"].create({"name": "Test Vendor B"})
        self.product1.seller_ids = [
            (0, 0, {"partner_id": vendor_a.id, "min_qty": 1, "price": 10}),
            (0, 0, {"partner_id": vendor_b.id, "min_qty": 1, "price": 20}),
        ]
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"]
                .create({"name": "Test Customer"})
                .id,
                "order_line": [
                    (0, 0, {"product_id": self.product1.id, "vendor_id": vendor_b.id})
                ],
            }
        )
        so.action_confirm()
        po = so._get_purchase_orders()
        self.assertEqual(len(po), 1, "A purchase order should have been created")
        self.assertEqual(po.partner_id, vendor_b)
