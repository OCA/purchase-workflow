# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.purchase_invoice_plan.tests.test_purchase_invoice_plan import (
    TestPurchaseInvoicePlan,
)


@tagged("post_install", "-at_install")
class TestPurchaseInvoicePlanRetention(TestPurchaseInvoicePlan):
    def setUp(self):
        super().setUp()

    def test_invoice_plan(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": True,
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 5
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.test_po_product.invoice_plan_ids), 5)
        self.test_po_product.payment_retention = "amount"
        self.test_po_product.amount_retention = 200.0
        # self.test_po_product.invoice_plan_ids[0].amount = 1000
        # self.test_po_product.invoice_plan_ids[4].amount = 3000
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # Receive all products
        receive = self.test_po_product.picking_ids.filtered(lambda l: l.state != "done")
        receive.move_ids_without_package.quantity_done = 10.0
        receive._action_done()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(ctx).create_invoices_by_plan()
        self.assertEqual(
            self.test_po_product.amount_total,
            sum(self.test_po_product.invoice_ids.mapped("amount_total")),
        )
        # Check invoices has retention following purchase
        self.assertEqual(
            list(set(self.test_po_product.invoice_ids.mapped("payment_retention"))),
            ["amount"],
        )
        self.assertEqual(
            list(set(self.test_po_product.invoice_ids.mapped("amount_retention"))),
            [200.0],
        )
