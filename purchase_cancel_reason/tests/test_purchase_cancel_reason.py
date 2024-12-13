# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseCancelReason(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Initialize test models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.CancelReason = cls.env["purchase.order.cancel.reason"]
        cls.PurchaseOrderCancel = cls.env["purchase.order.cancel"]

        # Create test reasons
        cls.reason = cls.CancelReason.create({"name": "Test Cancellation"})
        cls.reason_2 = cls.CancelReason.create({"name": "Another Reason"})

        # Create test partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
            }
        )

        # Create test product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
            }
        )

        # Create base purchase order
        cls.purchase_order = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner.id,
                "date_planned": fields.Datetime.now(),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "product_id": cls.product.id,
                            "product_qty": 1.0,
                            "product_uom": cls.product.uom_po_id.id,
                            "price_unit": 100.00,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )

        # Create additional purchase orders in different states
        cls.po_sent = cls.purchase_order.copy()
        cls.po_sent.write({"state": "sent"})

        cls.po_purchase = cls.purchase_order.copy()
        cls.po_purchase.write({"state": "purchase"})

        cls.po_done = cls.purchase_order.copy()
        cls.po_done.write({"state": "done"})

        cls.po_cancel = cls.purchase_order.copy()
        cls.po_cancel.write({"state": "cancel"})

    def test_purchase_order_cancel_reason(self):
        """Test basic purchase order cancellation with reason"""
        wizard = self.PurchaseOrderCancel.create({"reason_id": self.reason.id})
        wizard.with_context(
            active_model="purchase.order", active_ids=[self.purchase_order.id]
        ).confirm_cancel()

        self.assertEqual(
            self.purchase_order.state, "cancel", "Purchase order should be cancelled"
        )
        self.assertEqual(
            self.purchase_order.cancel_reason_id.id,
            self.reason.id,
            "Cancel reason should be set correctly",
        )

    def test_multiple_order_cancellation(self):
        """Test cancelling multiple purchase orders simultaneously"""
        orders_to_cancel = self.purchase_order + self.po_sent
        wizard = self.PurchaseOrderCancel.create({"reason_id": self.reason.id})
        wizard.with_context(
            active_model="purchase.order", active_ids=orders_to_cancel.ids
        ).confirm_cancel()

        for order in orders_to_cancel:
            self.assertEqual(
                order.state, "cancel", f"Order {order.name} should be cancelled"
            )
            self.assertEqual(
                order.cancel_reason_id.id,
                self.reason.id,
                f"Cancel reason should be set for order {order.name}",
            )

    def test_cancel_done_order(self):
        """Test cancellation of completed purchase order"""
        with self.assertRaises(ValidationError):
            self.po_done.action_open_cancel_wizard()

    def test_reason_update(self):
        """Test updating cancel reason"""
        # First cancel with initial reason
        wizard = self.PurchaseOrderCancel.create({"reason_id": self.reason.id})
        wizard.with_context(
            active_model="purchase.order", active_ids=[self.purchase_order.id]
        ).confirm_cancel()

        # Update reason
        self.purchase_order.write({"cancel_reason_id": self.reason_2.id})
        self.assertEqual(
            self.purchase_order.cancel_reason_id.id,
            self.reason_2.id,
            "Cancel reason should be updated",
        )

    def test_wizard_context_handling(self):
        """Test wizard behavior with different contexts"""
        wizard = self.PurchaseOrderCancel.create({"reason_id": self.reason.id})

        # Test missing active_ids
        result = wizard.with_context(active_model="purchase.order").confirm_cancel()
        self.assertEqual(
            result["type"],
            "ir.actions.act_window_close",
            "Should close window when no active_ids",
        )

        # Test wrong model
        result = wizard.with_context(
            active_model="res.partner", active_ids=[self.purchase_order.id]
        ).confirm_cancel()
        self.assertEqual(
            result["type"],
            "ir.actions.act_window_close",
            "Should close window for wrong model",
        )

    def test_cancel_wizard_action(self):
        """Test action to open cancel wizard"""
        action = self.purchase_order.action_open_cancel_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "purchase.order.cancel")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertIn(
            "default_purchase_order_ids",
            action["context"],
            "Context should include default purchase order IDs",
        )
