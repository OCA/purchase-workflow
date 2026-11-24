# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from unittest.mock import patch

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user


class TestPurchaseStockRestrictOverReceipt(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.product, cls.other_product = cls.env["product.product"].create(
            [{"name": name, "is_storable": True} for name in ("Ordered", "Other")]
        )

    def _order(self, quantity):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_qty": quantity}
                    )
                ],
            }
        )
        order.button_confirm()
        return order

    def _add_move(self, picking, product, quantity):
        picking.write(
            {
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": quantity,
                            "location_id": picking.location_id.id,
                            "location_dest_id": picking.location_dest_id.id,
                        }
                    )
                ]
            }
        )

    def _assert_refused(self, picking, message):
        # The savepoint undoes the refused validation, as the request would.
        with self.assertRaisesRegex(UserError, message), self.env.cr.savepoint():
            picking.button_validate()

    def test_receipt_is_limited_by_the_order_line(self):
        # The order line is the limit, not the demand of the transfer: raising
        # the demand, or adding a move of the same product, must not lift it.
        order = self._order(10.0)
        picking = order.picking_ids
        move = picking.move_ids
        picking.action_toggle_is_locked()
        move.write({"product_uom_qty": 11.0, "quantity": 11.0})
        self._assert_refused(picking, "more than the quantity ordered")
        move.write({"product_uom_qty": 10.0, "quantity": 10.0})
        self._add_move(picking, self.product, 1.0)
        self._assert_refused(picking, "more than the quantity ordered")
        (picking.move_ids - move).unlink()
        order.order_line.product_qty = 11.0
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(order.order_line.qty_received, 11.0)

    def test_unordered_product_is_refused_without_purchase_rights(self):
        # Odoo adds an order line for such a product, which a warehouse user
        # cannot do: the refusal must not surface as an access error.
        user = new_test_user(self.env, "warehouse", groups="stock.group_stock_user")
        order = self._order(10.0)
        picking = order.picking_ids
        self._add_move(picking, self.other_product, 1.0)
        # Read as the user would in a request of their own, with nothing cached.
        self.env.invalidate_all()
        self._assert_refused(picking.with_user(user), "not on the purchase order")
        self.assertEqual(len(order.order_line), 1)

    def test_return_of_an_over_received_line_is_allowed(self):
        # A line over received before the module was installed can only be
        # corrected by a return, which leaves it over received at first.
        order = self._order(10.0)
        picking = order.picking_ids
        picking.move_ids.quantity = 12.0
        with patch.object(
            self.registry["stock.move"],
            "_check_purchase_over_receipt",
            lambda self: None,
        ):
            picking.button_validate()
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        wizard.product_return_moves.write({"quantity": 1.0, "to_refund": True})
        return_picking = wizard._create_return()
        return_picking.button_validate()
        self.assertEqual(return_picking.state, "done")
        self.assertEqual(order.order_line.qty_received, 11.0)
