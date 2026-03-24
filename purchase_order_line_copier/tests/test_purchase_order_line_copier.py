# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseLineCopier(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.order_line = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )

    def test_01_copy_purchase_line_wizard(self):
        """Test duplicating a purchase order line via wizard."""
        wizard_vals = {
            "order_id": self.purchase_order.id,
        }
        wizard = (
            self.env["copy.purchase.line.wizard"]
            .with_context(default_order_id=self.purchase_order.id)
            .create(wizard_vals)
        )
        self.assertEqual(len(wizard.line_ids), 1, "Wizard should have 1 line loaded.")
        self.assertEqual(wizard.line_ids[0].line_id.id, self.order_line.id)
        wizard.line_ids[0].selected = True
        wizard.action_copy_lines()
        self.assertEqual(
            len(self.purchase_order.order_line),
            2,
            "Purchase order should have 2 lines now.",
        )
        new_line = self.purchase_order.order_line.filtered(
            lambda line: line.id != self.order_line.id
        )
        self.assertEqual(new_line.product_id.id, self.product.id)
        self.assertEqual(new_line.product_qty, 1.0)
        self.assertEqual(new_line.price_unit, 100.0)

    def test_02_copy_selected_lines(self):
        """Test duplicating only selected purchase order lines passed in context."""
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product.id,
                "product_qty": 2.0,
                "price_unit": 200.0,
            }
        )
        wizard = (
            self.env["copy.purchase.line.wizard"]
            .with_context(
                default_order_id=self.purchase_order.id,
                active_ids=[self.order_line.id],
                active_model="purchase.order.line",
            )
            .create({"order_id": self.purchase_order.id})
        )
        self.assertEqual(len(wizard.line_ids), 2, "Wizard should load both lines.")
        selected_lines = wizard.line_ids.filtered("selected").mapped("line_id")
        self.assertEqual(selected_lines, self.order_line)
        wizard.action_copy_lines()
        self.assertEqual(
            len(self.purchase_order.order_line), 3, "Total lines should be 3."
        )
        self.assertEqual(
            self.purchase_order.order_line.mapped("product_qty"), [1.0, 2.0, 1.0]
        )
