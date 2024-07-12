# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
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
        self.product1 = self.env.ref("product.product_product_13")
        self.company2 = self.env["res.company"].create({"name": "Test company"})
        self.picking_type2 = self.env["stock.picking.type"].search(
            [("code", "=", "incoming")]
        )

    def _create_pr(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product1.id,
                        "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                        "product_qty": 5.0,
                    },
                )
            ],
        }
        purchase_request = self.purchase_request.create(vals)
        return purchase_request

    def test_01_purchase_request_to_purchase_requisition(self):
        purchase_request = self._create_pr()
        # Test unlink pr line
        purchase_request.line_ids.unlink()
        purchase_request = self._create_pr()
        purchase_request_line = purchase_request.line_ids
        # Test create TE from PR
        wiz1 = self.wiz.with_context(
            active_model="purchase.request",
        ).create({})
        self.assertFalse(wiz1.item_ids)
        wiz1 = self.wiz.with_context(
            active_model="purchase.request",
            active_ids=[purchase_request.id],
        ).create({})
        # Test onchange qty will change to 1
        self.product1.description_purchase = "Test description purchase"
        wiz1.item_ids.onchange_product_id()
        self.assertEqual(wiz1.item_ids.product_qty, 1)
        self.assertEqual(len(wiz1.item_ids), 1)
        # Test create TE from PR Line
        wiz2 = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,
        ).create({})
        self.assertEqual(len(wiz2.item_ids), 1)
        # check PR or PR Line when create TE must be equal
        self.assertEqual(wiz1.item_ids.request_id, wiz2.item_ids.request_id)
        # Test qty < 1
        with self.assertRaises(UserError):
            wiz2.item_ids.product_qty = 0.0
            wiz2.make_purchase_requisition()
        wiz2.make_purchase_requisition()
        # check PR link to TE must have 1
        self.assertEqual(purchase_request.requisition_count, 1)
        action = purchase_request.action_view_purchase_requisition()
        self.assertEqual(
            action["res_id"],
            purchase_request.line_ids.mapped("requisition_lines.requisition_id").id,
        )
        self.assertTrue(
            len(purchase_request_line.requisition_lines.ids) == 1,
            "Should have one purchase agreement line created",
        )
        # Not edit after created TE
        self.assertFalse(purchase_request.line_ids.is_editable)
        self.assertEqual(
            purchase_request.line_ids.requisition_qty,
            purchase_request.line_ids.product_qty,
        )
        # Test delete line PR after created TE
        with self.assertRaises(UserError):
            purchase_request.line_ids.unlink()
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
        # check TE link to PR must have 1
        self.assertEqual(requisition.purchase_request_count, 1)
        action = requisition.action_view_purchase_request()
        self.assertEqual(
            action["res_id"],
            requisition.line_ids.purchase_request_lines.request_id.id,
        )
        self.assertTrue(requisition.line_ids.has_purchase_request_lines)
        # check TE Line link to PR Line
        action = requisition.line_ids.action_open_request_line_tree_view()
        self.assertEqual(
            action["domain"][0][2],
            requisition.line_ids.purchase_request_lines.ids,
        )
        # Check state
        self.assertEqual(purchase_request.line_ids.requisition_state, "draft")
        requisition.action_cancel()
        self.assertEqual(purchase_request.line_ids.requisition_state, "cancel")
        requisition.action_in_progress()
        self.assertEqual(purchase_request.line_ids.requisition_state, "in_progress")
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
        # close TE
        requisition.action_done()
        self.assertEqual(purchase_request.line_ids.requisition_state, "done")

    def test_02_multi_purchase_request_to_purchase_requisition(self):
        purchase_request1 = self._create_pr()
        purchase_request2 = self._create_pr()
        # 2 PR Line (diff PR) create 1 TE
        purchase_request_line = purchase_request1.line_ids + purchase_request2.line_ids
        wiz = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=purchase_request_line.ids,
        ).create({})
        # Test multi company in 1 TE
        pr_line = wiz.item_ids[-1].line_id
        with self.assertRaises(UserError):
            pr_line.company_id = self.company2
            wiz.make_purchase_requisition()
        # Test multi picking in 1 TE
        picking_type2 = self.picking_type2.filtered(
            lambda l: l != pr_line.request_id.picking_type_id
        )
        with self.assertRaises(UserError):
            pr_line.request_id.picking_type_id = picking_type2[0]
            wiz.make_purchase_requisition()
        wiz.make_purchase_requisition()
        requisition = purchase_request_line.requisition_lines.requisition_id
        action = requisition.action_view_purchase_request()
        self.assertEqual(
            action["domain"][0][2],
            requisition.mapped("line_ids.purchase_request_lines.request_id").ids,
        )
        # Test add old TE into new TE
        requisition = purchase_request1.line_ids.requisition_lines.requisition_id
        wiz = self.wiz.with_context(
            active_model="purchase.request",
            active_ids=purchase_request1.ids,
        ).create({"purchase_requisition_id": requisition.id})
        wiz.make_purchase_requisition()
        # 1 PR create 2 TE
        wiz = self.wiz.with_context(
            active_model="purchase.request",
            active_ids=purchase_request1.ids,
        ).create({})
        wiz.make_purchase_requisition()
        purchase_request1.action_view_purchase_requisition()

    def test_03_product_request_requisition(self):
        with self.assertRaises(UserError):
            self.product1.write(
                {
                    "purchase_request": True,
                    "purchase_requisition": "tenders",
                }
            )
        self.product1.write(
            {
                "purchase_request": False,
                "purchase_requisition": "tenders",
            }
        )
