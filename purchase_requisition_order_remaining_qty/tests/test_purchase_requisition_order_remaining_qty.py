# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequisitionOrderRemainingQty(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.requisition_type = cls.env["purchase.requisition.type"].create(
            {"name": "Test type", "quantity_copy": "remaining_qty"}
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.user = cls.env.ref("base.user_admin")

    def _create_purchase_requisition(self):
        requisition_form = Form(self.env["purchase.requisition"])
        requisition_form.type_id = self.requisition_type
        requisition_form.user_id = self.user
        requisition_form.vendor_id = self.partner
        with requisition_form.line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 5
            line_form.price_unit = 1
        return requisition_form.save()

    def action_purchase_requisition_to_so(self, requisition_id):
        purchase_form = Form(
            self.env["purchase.order"].with_context(
                default_requisition_id=requisition_id
            )
        )
        return purchase_form.save()

    def test_purchase_requisition_remaining_qty(self):
        requisition = self._create_purchase_requisition()
        requisition_line = requisition.line_ids.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(requisition_line.proposed_qty, 0)
        # New order with qty: 5. Example: product_qty: 5, proposed_qty: 0
        order = self.action_purchase_requisition_to_so(requisition.id)
        order.button_confirm()
        order_line = order.order_line.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(order_line.product_qty, 5)
        self.assertEqual(requisition_line.proposed_qty, 5)
        # Update qty in order line need to recompute proposed_qty
        order_line.product_qty = 3
        self.assertEqual(requisition_line.proposed_qty, 3)
        # New order with qty: 2. Example: product_qty: 5, proposed_qty: 3
        order = self.action_purchase_requisition_to_so(requisition.id)
        order_line = order.order_line.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(order_line.product_qty, 2)
        self.assertEqual(requisition_line.proposed_qty, 5)
        # New order without line. Example: product_qty: 5, proposed_qty: 5
        order = self.action_purchase_requisition_to_so(requisition.id)
        self.assertEqual(len(order.order_line), 0)
        # Update product_qty in requisition line
        requisition_line.product_qty = 6
        # New order with qty: 1. Example: product_qty: 6, proposed_qty: 5
        order = self.action_purchase_requisition_to_so(requisition.id)
        order_line = order.order_line.filtered(lambda x: x.product_id == self.product)
        self.assertEqual(order_line.product_qty, 1)
