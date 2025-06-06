from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseReceptionNotify(TransactionCase):
    def setUp(self):
        super().setUp()
        self.purchase_order_model = self.env["purchase.order"]
        self.purchase_order_line_model = self.env["purchase.order.line"]
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.uom_model = self.env["uom.uom"]
        self.stock_picking_model = self.env["stock.picking"]

        # Partners
        self.partner = self.partner_model.sudo().create({"name": "Partner 1"})

        # UOM
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        # Product
        self.product = self.product_model.sudo().create(
            {
                "name": "Product Test",
                "uom_id": self.uom_unit.id,
                "purchase_method": "purchase",
            }
        )

        # Purchase Order
        self.purchase_order = self.purchase_order_model.create(
            {"partner_id": self.partner.id}
        )
        self.purchase_order_line = self.purchase_order_line_model.sudo().create(
            {
                "date_planned": Datetime.now(),
                "name": "PO01",
                "order_id": self.purchase_order.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "price_unit": 1.0,
                "product_qty": 5.0,
            }
        )
        self.purchase_order.button_confirm()

    def test_action_done_message_post(self):
        """Test that the _action_done method posts the correct message."""
        # Validate picking to trigger `_action_done`
        picking = self.purchase_order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty  # Set quantity as done
        picking.button_validate()

        # Assert that a message was posted on the Purchase Order
        self.assertTrue(
            self.purchase_order.message_ids,
            "No message was posted on the Purchase Order.",
        )

        # Check the last message content
        last_message = self.purchase_order.message_ids[0]
        self.assertIn(
            "Receipt confirmation",
            last_message.body,
            "The confirmation message is not correctly posted.",
        )
        self.assertIn(
            "The following items have now been received",
            last_message.body,
            "The detailed message content is missing.",
        )

        # Check that the product name and quantity are in the message
        self.assertIn(
            self.product.display_name,
            last_message.body,
            "The product name is not included in the message.",
        )
        self.assertIn(
            str(self.purchase_order_line.product_qty),
            last_message.body,
            "The product quantity is not included in the message.",
        )
        self.assertIn(
            self.uom_unit.name,
            last_message.body,
            "The unit of measure is not included in the message.",
        )

    def test_action_done_empty_purchase_dict(self):
        """Test that _action_done handles the case when purchase_dict is empty."""
        # Get the picking related to the purchase order
        picking = self.purchase_order.picking_ids

        # Simulate a case where no moves are linked to purchase lines
        for move in picking.move_ids:
            move.write({"purchase_line_id": None})

        # Validate the picking to trigger _action_done
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()

        # Ensure the purchase_dict line is covered by asserting no crash occurred
        self.assertTrue(
            picking.state == "done",
            "Picking should be completed successfully "
            "even with an empty purchase_dict.",
        )

        # Check that no custom message was posted for receipt confirmation
        last_message = self.purchase_order.message_ids[0]
        self.assertNotIn(
            "Receipt confirmation",
            last_message.body,
            "A receipt confirmation message should not be posted "
            "when purchase_dict is empty.",
        )
        self.assertIn(
            "Purchase Order created",
            last_message.body,
            "The default Purchase Order creation message should still exist.",
        )
