# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, SavepointCase


class TestPurchaseOrderLineReceiptStatus(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].search([], limit=1)
        cls.product = cls.env["product.product"].search(
            [("type", "=", "product")], limit=1
        )

    @classmethod
    def _create_purchase_order(cls):
        purchase_form = Form(cls.env["purchase.order"])
        purchase_form.partner_id = cls.partner
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_qty = 10
        return purchase_form.save()

    def test_line_receipt_status(self):
        order = self._create_purchase_order()
        line = order.order_line
        self.assertEqual(line.receipt_status, "nothing")
        order.button_confirm()
        self.assertEqual(line.receipt_status, "pending")
        receipt = order.picking_ids
        receipt.move_ids_without_package.quantity_done = 5
        # Create backorder
        backorder_action_dict = receipt.button_validate()
        backorder_wizard = (
            self.env[(backorder_action_dict.get("res_model"))]
            .with_context(**backorder_action_dict["context"])
            .create({})
        )
        backorder_wizard.process()
        self.assertEqual(len(order.picking_ids), 2)
        self.assertEqual(line.receipt_status, "partial")
        backorder = order.picking_ids - receipt
        backorder.move_ids_without_package.quantity_done = 2
        # Do not create backorder
        backorder_action_dict = backorder.button_validate()
        backorder_wizard = (
            self.env[(backorder_action_dict.get("res_model"))]
            .with_context(**backorder_action_dict["context"])
            .create({})
        )
        backorder_wizard.process_cancel_backorder()
        self.assertEqual(len(order.picking_ids), 2)
        self.assertEqual(line.receipt_status, "full")
