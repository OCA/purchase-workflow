# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPurchaseRequestToRequisition(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestToRequisition, self).setUp()
        self.purchase_request = self.env["purchase.request"]
        self.purchase_request_line = self.env["purchase.request.line"]
        self.wiz = self.env["purchase.request.line.make.purchase.requisition"]
        self.purchase_order = self.env["purchase.order"]

    def test_purchase_request_to_purchase_requisition(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request.id,
            "product_id": self.env.ref("product.product_product_13").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        wiz = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,
        ).create({})
        wiz.make_purchase_requisition()
        self.assertTrue(
            len(purchase_request_line.requisition_lines.ids) == 1,
            "Should have one purchase agreement line created",
        )
        requisition = purchase_request_line.requisition_lines.requisition_id
        self.assertEqual(
            len(purchase_request.line_ids),
            len(requisition.line_ids),
            "Should have the same lines",
        )
        requisition_line = requisition.line_ids
        self.assertEqual(
            requisition_line.product_id.id,
            purchase_request_line.product_id.id,
            "Should have the same products",
        )
        self.assertEqual(
            purchase_request.state, requisition.state, "Should have the same state"
        )
        requisition.action_in_progress()
        requisition.action_open()
        # Create Purchase from Agreement
        purchase = self.purchase_order.create(
            {
                "partner_id": self.env.ref("base.res_partner_12").id,
                "requisition_id": requisition.id,
            }
        )
        purchase._onchange_requisition_id()
        purchase.button_confirm()
        self.assertEqual(
            len(purchase.order_line.purchase_request_lines),
            1,
            "Should have a link between order lines and request lines",
        )
