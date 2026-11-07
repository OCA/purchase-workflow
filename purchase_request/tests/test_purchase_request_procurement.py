# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields
from odoo.tests import common


class TestPurchaseRequestProcurement(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # Get required Model
        self.pr_model = self.env["purchase.request"]
        self.prl_model = self.env["purchase.request.line"]
        self.product_uom_model = self.env["uom.uom"]
        self.location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")

        # Get required Model data
        self.route_buy = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.product_1 = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_request": True,
                "route_ids": [(4, self.route_buy.id)],
            }
        )
        self.rule_buy = self.route_buy.rule_ids.filtered(
            lambda rule: rule.location_dest_id == self.location
        )
        # Create Supplier
        self.supplier = self.env["res.partner"].create(
            {"name": "Supplier", "is_company": True, "company_id": False}
        )

        # Add supplier to product_1
        self.product_1.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "price": 100.0,
                            "company_id": False,
                        },
                    )
                ]
            }
        )

    def _procurement_group_run(self, origin, product, qty):
        """Create an outgoing move and procure it"""
        move = self.env["stock.move"].create(
            {
                "reservation_date": fields.Datetime.now(),
                "location_dest_id": self.customer_location.id,
                "location_id": self.location.id,
                "origin": origin,
                "procure_method": "make_to_order",
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "route_ids": [(4, self.route_buy.id)],
            }
        )
        move._action_confirm()
        return move

    def test_orderpoint(self):
        """Purchase request quantity is reflected in the orderpoint forecasted qty"""
        qty = 5
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": __name__,
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "location_id": self.location.id,
                "product_id": self.product_1.id,
                "product_min_qty": 1,
                "product_max_qty": qty,
            }
        )
        self.env["stock.rule"].run_scheduler()
        self.assertEqual(
            self.env["purchase.request"]
            .search([("product_id", "=", self.product_1.id)])
            .line_ids.product_qty,
            qty,
        )
        self.assertEqual(orderpoint.qty_forecast, qty)

    def test_procure_purchase_request(self):
        """A request line is created from a procured move"""
        move = self._procurement_group_run(
            "Test Purchase Request Procurement",
            self.product_1,
            10,
        )
        self.assertTrue(move.created_purchase_request_line_id)
        pr = move.created_purchase_request_line_id.request_id
        self.assertTrue(pr.to_approve_allowed)
        self.assertEqual(pr.origin, "Test Purchase Request Procurement")

        # Now cancel the move. An activity is created on the request.
        activity = self.env.ref("mail.mail_activity_data_todo")
        self.env["mail.activity"].search(
            [("activity_type_id", "=", activity.id)]
        ).unlink()
        self.assertFalse(move.created_purchase_request_line_id.request_id.activity_ids)
        move._action_cancel()
        self.assertTrue(move.created_purchase_request_line_id.request_id.activity_ids)

    def test_origin(self):
        """The purchase request origin reflects the origins of each procurement"""
        move = self._procurement_group_run("Test Origin", self.product_1, 10)
        pr = move.created_purchase_request_line_id.request_id
        self.assertEqual(pr.origin, "Test Origin")

        # A new procurement origin is added to the request origin
        move2 = self._procurement_group_run("Test, Split", self.product_1, 10)
        self.assertEqual(move2.created_purchase_request_line_id.request_id, pr)
        self.assertEqual(pr.origin, "Test Origin, Test, Split")

        # An empty procurement origin is not added to the request origin
        move3 = self._procurement_group_run(False, self.product_1, 10)
        self.assertEqual(move3.created_purchase_request_line_id.request_id, pr)
        self.assertEqual(pr.origin, "Test Origin, Test, Split")

        # An existing procurement origin is not added to the request origin
        move4 = self._procurement_group_run("Split", self.product_1, 10)
        self.assertEqual(move4.created_purchase_request_line_id.request_id, pr)
        self.assertEqual(pr.origin, "Test Origin, Test, Split")

    def test_orderpoint_replenishment_notification(self):
        """Check replenishment notification returns a client action linking to the purchase request."""
        qty = 10
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "OP Notification Test",
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "location_id": self.location.id,
                "product_id": self.product_1.id,
                "product_min_qty": 1,
                "product_max_qty": qty,
            }
        )
        po_count_before = self.env["purchase.order"].search_count([])
        notification = orderpoint.action_replenish()

        # 1. Assert notification action and params
        self.assertTrue(notification)
        self.assertEqual(notification.get("type"), "ir.actions.client")
        self.assertEqual(notification.get("tag"), "display_notification")
        params = notification.get("params", {})
        self.assertTrue(params.get("sticky"))

        # 2. Assert purchase request line created and linked
        pr_line = self.env["purchase.request.line"].search(
            [("orderpoint_id", "=", orderpoint.id)], limit=1
        )
        self.assertTrue(pr_line)
        pr = pr_line.request_id
        expected_url = (
            f"/odoo/action-purchase_request.purchase_request_form_action/{pr.id}"
        )
        links = params.get("links", [])
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].get("url"), expected_url)
        self.assertEqual(links[0].get("label"), pr.display_name)

        # 3. Assert NO purchase order was created
        po_count_after = self.env["purchase.order"].search_count([])
        self.assertEqual(po_count_before, po_count_after)

        # 4. Assert notification when reusing draft purchase request
        product_2 = self.env["product.product"].create(
            {
                "name": "Second PR product",
                "is_storable": True,
                "purchase_request": True,
                "route_ids": [(4, self.route_buy.id)],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "price": 50.0,
                            "company_id": False,
                        },
                    )
                ],
            }
        )
        orderpoint_2 = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "OP Notification Test 2",
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "location_id": self.location.id,
                "product_id": product_2.id,
                "product_min_qty": 1,
                "product_max_qty": qty,
            }
        )
        notification_2 = orderpoint_2.action_replenish()
        self.assertTrue(notification_2)
        links_2 = notification_2.get("params", {}).get("links", [])
        self.assertEqual(len(links_2), 1)
        self.assertEqual(links_2[0].get("url"), expected_url)

        # 5. Assert standard buy product preserves standard PO notification
        product_std = self.env["product.product"].create(
            {
                "name": "Standard PO product",
                "is_storable": True,
                "purchase_request": False,
                "route_ids": [(4, self.route_buy.id)],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "price": 50.0,
                            "company_id": False,
                        },
                    )
                ],
            }
        )
        orderpoint_std = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "OP Standard Test",
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "location_id": self.location.id,
                "product_id": product_std.id,
                "product_min_qty": 1,
                "product_max_qty": qty,
            }
        )
        notification_std = orderpoint_std.action_replenish()
        self.assertTrue(notification_std)
        links_std = notification_std.get("params", {}).get("links", [])
        self.assertEqual(len(links_std), 1)
        self.assertIn(
            "/odoo/action-purchase.action_rfq_form/", links_std[0].get("url", "")
        )
        self.assertFalse(notification_std.get("params", {}).get("sticky"))
