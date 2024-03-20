# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseLineCancel(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["purchase.order.line.stock.move.cancel"]
        cls.purchase_obj = cls.env["purchase.order"]
        cls.supplier = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "product",
            }
        )

    @classmethod
    def _create_purchase_order(cls):
        with Form(cls.purchase_obj) as purchase_form:
            purchase_form.partner_id = cls.supplier
            with purchase_form.order_line.new() as line_form:
                line_form.product_id = cls.product_1
                line_form.product_qty = 10.0
                line_form.price_unit = 1.0
            with purchase_form.order_line.new() as line_form:
                line_form.product_id = cls.product_2
                line_form.product_qty = 15.0
                line_form.price_unit = 1.0

        cls.purchase = purchase_form.save()

    def test_purchase_line_cancel(self):
        """
        Create a Purchase Order and confirm it
        Check moves have been generated
        Check we can cancel move for product 1
        Cancel line 1
        Check move has been cancelled
        Check message contains line name
        """
        self._create_purchase_order()
        self.purchase.button_confirm()
        self.assertEqual(self.purchase.state, "purchase")
        self.assertTrue(self.purchase.order_line.move_ids)
        self.assertEqual(
            self.purchase.order_line.move_ids.mapped("state"), ["assigned", "assigned"]
        )
        line_1 = self.purchase.order_line.filtered(
            lambda line: line.product_id == self.product_1
        )
        self.assertTrue(line_1.can_cancel_moves)
        messages_before = self.purchase.message_ids
        line_1._cancel_moves()
        self.assertEqual(
            line_1.move_ids.state,
            "cancel",
        )
        self.assertFalse(line_1.can_cancel_moves)
        new_messages = self.purchase.message_ids - messages_before

        self.assertTrue(new_messages)
        self.assertIn("Lines that have been cancelled", str(new_messages.body))
        self.assertIn(line_1.display_name, str(new_messages.body))

    def test_purchase_line_cancel_wizard(self):
        """
        Create a Purchase Order and confirm it
        Check moves have been generated
        Check we can cancel move for product 1
        Cancel line 1
        Check move has been cancelled
        Check message contains line name
        """
        self._create_purchase_order()
        self.purchase.button_confirm()
        self.assertEqual(self.purchase.state, "purchase")
        self.assertTrue(self.purchase.order_line.move_ids)
        self.assertEqual(
            self.purchase.order_line.move_ids.mapped("state"), ["assigned", "assigned"]
        )
        line_1 = self.purchase.order_line.filtered(
            lambda line: line.product_id == self.product_1
        )
        self.assertTrue(line_1.can_cancel_moves)
        messages_before = self.purchase.message_ids

        # Create the wizard
        wizard = self.wizard_obj.create(
            {"purchase_line_ids": [Command.set(line_1.ids)]}
        )

        self.assertEqual(
            wizard.purchase_line_ids,
            line_1,
        )
        wizard.process()
        self.assertEqual(
            line_1.move_ids.state,
            "cancel",
        )
        self.assertFalse(line_1.can_cancel_moves)
        new_messages = self.purchase.message_ids - messages_before

        self.assertTrue(new_messages)
        self.assertIn("Lines that have been cancelled", str(new_messages.body))
        self.assertIn(line_1.display_name, str(new_messages.body))

    def test_purchase_line_cancel_wizard_action(self):
        """
        Create a Purchase Order and confirm it
        Check moves have been generated
        Check we can cancel move for product 1
        Then try the action
        """
        self._create_purchase_order()
        self.purchase.button_confirm()
        self.assertEqual(self.purchase.state, "purchase")
        self.assertTrue(self.purchase.order_line.move_ids)
        self.assertEqual(
            self.purchase.order_line.move_ids.mapped("state"), ["assigned", "assigned"]
        )
        line_1 = self.purchase.order_line.filtered(
            lambda line: line.product_id == self.product_1
        )
        self.assertTrue(line_1.can_cancel_moves)

        res = line_1.action_cancel_moves()

        wizard = self.wizard_obj.browse(res.get("res_id"))
        self.assertIn(wizard.purchase_line_ids, line_1)
