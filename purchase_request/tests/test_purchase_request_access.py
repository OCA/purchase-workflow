# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequestAccess(BaseCommon):
    _test_user_groups = (
        "purchase_request.group_purchase_request_manager",
        "purchase.group_purchase_manager",
        "stock.group_stock_manager",
        "product.group_product_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.picking_type = cls.env.ref("stock.picking_type_in")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.route_buy.product_selectable = True
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Requested Product",
                "type": "consu",
                "is_storable": True,
                "purchase_request": True,
                "route_ids": [Command.link(cls.route_buy.id)],
                "seller_ids": [Command.create({"partner_id": cls.supplier.id})],
            }
        )
        cls.service = cls.env["product.product"].create(
            {"name": "Requested Service", "type": "service"}
        )
        pr_user = "purchase_request.group_purchase_request_user"
        cls.requester = new_test_user(cls.env, "pr_requester", groups=pr_user)
        cls.pr_stock_user = new_test_user(
            cls.env, "pr_stock_user", groups=f"{pr_user},stock.group_stock_user"
        )
        cls.pr_purchase_user = new_test_user(
            cls.env,
            "pr_purchase_user",
            groups=f"{pr_user},purchase.group_purchase_user",
        )
        cls.purchase_user = new_test_user(
            cls.env, "purchase_user", groups="purchase.group_purchase_user"
        )
        cls.stock_user = new_test_user(
            cls.env, "stock_user", groups="stock.group_stock_user"
        )
        cls.request = cls._create_request(cls.requester, cls.product, 5.0)

    @classmethod
    def _create_request(cls, user, product, qty):
        return cls.env["purchase.request"].create(
            {
                "requested_by": user.id,
                "picking_type_id": cls.picking_type.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_id": cls.uom_unit.id,
                            "product_qty": qty,
                        }
                    )
                ],
            }
        )

    def _create_purchase_order(self, request_line):
        request_line.request_id.button_approved()
        wizard = (
            self.env["purchase.request.line.make.purchase.order"]
            .with_context(
                active_model="purchase.request.line", active_ids=request_line.ids
            )
            .create({"supplier_id": self.supplier.id})
        )
        wizard.item_ids.product_qty = request_line.product_qty
        wizard.make_purchase_order()
        return request_line.purchase_lines.order_id.sorted("id")[-1:]

    def _receive(self, purchase, user):
        picking = purchase.picking_ids.with_user(user)
        picking.move_ids.write({"quantity": 5.0, "picked": True})
        picking.button_validate()

    def test_request_user_only_sees_own_requests(self):
        """Being also an Inventory or Purchase User does not give access to
        the requests of other users"""
        for user in self.pr_stock_user | self.pr_purchase_user:
            requests = self.env["purchase.request"].with_user(user)
            self.assertFalse(requests.search([("id", "=", self.request.id)]))
            with self.assertRaises(AccessError):
                self.request.with_user(user).read(["name"])
            with self.assertRaises(AccessError):
                self.request.line_ids.with_user(user).write({"product_qty": 1.0})
            # Own requests can be modified
            own_request = self._create_request(user, self.product, 1.0)
            own_request.line_ids.with_user(user).write({"product_qty": 2.0})
            # Followed requests can be read, not modified
            self.request.message_subscribe(partner_ids=user.partner_id.ids)
            self.request.with_user(user).read(["name"])
            with self.assertRaises(AccessError):
                self.request.line_ids.with_user(user).write({"product_qty": 1.0})

    def test_users_without_request_group(self):
        """Purchase and Inventory Users need a Purchase Request group to
        access the requests"""
        for user in self.purchase_user | self.stock_user:
            self.assertFalse(self.request.with_user(user).has_access("read"))
            self.assertFalse(self.request.line_ids.with_user(user).has_access("read"))

    def test_purchase_and_receipt(self):
        """Purchase and Inventory Users process the orders of the requests"""
        request_line = self.request.line_ids
        purchase = self._create_purchase_order(request_line)
        purchase.order_line.price_unit = 10.0
        # The order can be opened, the request lines of other users are hidden
        for user in self.purchase_user | self.pr_purchase_user:
            order_line = purchase.order_line.with_user(user)
            order_line.web_read(
                {
                    "purchase_request_lines": {
                        "fields": {"name": {}, "product_qty": {}, "request_id": {}}
                    }
                }
            )
            self.assertFalse(order_line.purchase_request_lines)
        purchase = purchase.with_user(self.purchase_user)
        self.env.invalidate_all()
        purchase.button_confirm()
        self.assertEqual(request_line.purchase_state, "purchase")
        self.assertIn(purchase.name, self.request.message_ids[0].body)
        self.env.invalidate_all()
        moves = purchase.picking_ids.move_ids.with_user(self.stock_user)
        moves.web_read(
            {
                "purchase_request_allocation_ids": {
                    "fields": {"purchase_request_line_id": {"fields": {}}}
                },
            }
        )
        self.env.invalidate_all()
        self._receive(purchase, self.stock_user)
        self.assertEqual(request_line.qty_done, 5.0)

    def test_confirm_order_of_done_request_line(self):
        """The check on done request lines also works for Purchase Users"""
        request_line = self.request.line_ids
        purchase = self._create_purchase_order(request_line)
        purchase2 = self._create_purchase_order(request_line)
        self.assertNotEqual(purchase, purchase2)
        purchase.button_confirm()
        self._receive(purchase, self.env.user)
        self.assertEqual(request_line.purchase_state, "done")
        self.env.invalidate_all()
        with self.assertRaisesRegex(UserError, "already been completed"):
            purchase2.with_user(self.purchase_user).button_confirm()
        self.env.invalidate_all()
        purchase2.with_user(self.purchase_user).button_cancel()
        purchase2.with_user(self.purchase_user).unlink()
        self.assertEqual(len(request_line.purchase_request_allocation_ids), 1)

    def test_service_received_by_purchase_user(self):
        request = self._create_request(self.requester, self.service, 2.0)
        purchase = self._create_purchase_order(request.line_ids)
        purchase.button_confirm()
        self.env.invalidate_all()
        purchase.order_line.with_user(self.purchase_user).write({"qty_received": 2.0})
        self.assertEqual(request.line_ids.qty_done, 2.0)

    def test_calc_new_qty_restricted_user(self):
        """The quantity of a purchase line includes the request lines of
        other users"""
        purchase = self._create_purchase_order(self.request.line_ids)
        own_request = self._create_request(self.pr_purchase_user, self.product, 3.0)
        self.env.invalidate_all()
        qty = (
            self.env["purchase.request.line"]
            .with_user(self.pr_purchase_user)
            ._calc_new_qty(
                own_request.line_ids.with_user(self.pr_purchase_user),
                po_line=purchase.order_line.with_user(self.pr_purchase_user),
            )
        )
        self.assertEqual(qty, 5.0)

    def test_orderpoint_quantity_in_progress(self):
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "location_id": self.location.id,
                "product_id": self.product.id,
                "product_min_qty": 1.0,
                "product_max_qty": 10.0,
            }
        )
        self.request.line_ids.orderpoint_id = orderpoint
        self.env.invalidate_all()
        qty = orderpoint.with_user(self.stock_user)._quantity_in_progress()
        self.assertEqual(qty[orderpoint.id], 5.0)

    def test_procurement_by_stock_user(self):
        """Inventory Users can run the procurements that create requests"""
        move = (
            self.env["stock.move"]
            .with_user(self.stock_user)
            .create(
                {
                    "location_id": self.location.id,
                    "location_dest_id": self.env.ref(
                        "stock.stock_location_customers"
                    ).id,
                    "procure_method": "make_to_order",
                    "product_id": self.product.id,
                    "product_uom_qty": 3.0,
                    "route_ids": [Command.link(self.route_buy.id)],
                }
            )
        )
        move._action_confirm()
        request_line = move.sudo().created_purchase_request_line_id
        self.assertEqual(request_line.product_qty, 3.0)
        self.env.invalidate_all()
        move._action_cancel()
        self.assertTrue(request_line.request_id.activity_ids)
