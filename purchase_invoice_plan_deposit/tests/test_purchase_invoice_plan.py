# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError
from odoo.tests.common import Form

from odoo.addons.purchase_deposit.tests.test_purchase_deposit import TestPurchaseDeposit
from odoo.addons.purchase_invoice_plan.tests.test_purchase_invoice_plan import (
    TestPurchaseInvoicePlan,
)


class TestPurchaseInvoicePlanDeposit(TestPurchaseInvoicePlan, TestPurchaseDeposit):
    def setUp(self):
        super().setUp()
        self.deposit_model = self.env["purchase.advance.payment.inv"]

    def test_invoice_plan_with_advance(self):
        self.test_service.purchase_method = "purchase"  # invoiced by order qty
        ctx = {
            "active_id": self.test_po_service.id,
            "active_ids": [self.test_po_service.id],
            "all_remain_invoices": True,
            "create_bills": True,
        }
        # Create purchase plan with advance
        num_installment = 5
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = num_installment
            p.advance = True
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        # Check invoice plan created
        self.assertTrue(self.test_po_service.invoice_plan_ids)
        with self.assertRaises(UserError):
            self.test_po_service.invoice_plan_ids[1].invoice_type = "advance"
            self.test_po_service._check_invoice_plan_ids()
        # If advance percent is not filled, show error
        advance_line = self.test_po_service.invoice_plan_ids.filtered(
            lambda l: l.invoice_type == "advance"
        )
        self.assertEqual(len(advance_line), 1, "No one advance line")
        # Add 10% to advance
        advance_line.percent = 10
        # Confirm PO and cereate invoices
        self.test_po_service.button_confirm()
        self.assertEqual(self.test_po_service.state, "purchase")
        self.assertTrue(self.test_po_service.ip_invoice_plan)
        # Check there is deposit installment must register deposit first
        with self.assertRaises(UserError):
            self.test_po_service.action_create_invoice()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(ctx).create_invoices_by_plan()
        # Valid number of invoices, including advance
        invoices = self.test_po_service.invoice_ids
        self.assertEqual(
            len(invoices), num_installment + 1, "Wrong number of invoice created"
        )
        # Validate advance amount, which is 10% of purhcase order
        adv_invoice = (
            invoices.mapped("invoice_line_ids")
            .filtered(lambda l: l.purchase_line_id.is_deposit and l.quantity == 1)
            .mapped("move_id")
        )
        self.assertEqual(
            adv_invoice.amount_total,
            self.test_po_service.amount_total * 0.1,
            "Wrong advance amount",
        )
        # Valid total quantity of invoices (exclude Advance line), must be equal to 1
        quantity = sum(
            invoices.mapped("invoice_line_ids")
            .filtered(lambda l: l.product_id == self.test_service)
            .mapped("quantity")
        )
        self.assertEqual(quantity, 1, "Wrong number of total invoice quantity")
