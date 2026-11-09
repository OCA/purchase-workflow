# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import Command, fields

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequestProcurement(BaseCommon):
    _test_user_groups = (
        "purchase_request.group_purchase_request_manager",
        "purchase.group_purchase_manager",
        "stock.group_stock_manager",
        "product.group_product_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get required Model
        cls.pr_model = cls.env["purchase.request"]
        cls.prl_model = cls.env["purchase.request.line"]
        cls.product_uom_model = cls.env["uom.uom"]
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # Get required Model data
        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.route_buy.product_selectable = True
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_request": True,
                "route_ids": [Command.link(cls.route_buy.id)],
            }
        )
        cls.rule_buy = cls.route_buy.rule_ids.filtered(
            lambda rule: rule.location_dest_id == cls.location
        )
        # Create Supplier
        cls.supplier = cls.env["res.partner"].create(
            {"name": "Supplier", "is_company": True, "company_id": False}
        )

        # Add supplier to product_1
        cls.product_1.write(
            {
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.supplier.id,
                            "price": 100.0,
                            "company_id": False,
                        }
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
                "uom_id": product.uom_id.id,
                "product_uom_qty": qty,
                "route_ids": [Command.link(self.route_buy.id)],
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
