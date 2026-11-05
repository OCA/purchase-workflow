# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.purchase_deposit.tests.test_purchase_deposit import TestPurchaseDeposit
from odoo.addons.purchase_invoice_plan.tests.test_purchase_invoice_plan import (
    TestPurchaseInvoicePlan,
)


class TestPurchaseInvoicePlanDeposit(TestPurchaseInvoicePlan, TestPurchaseDeposit):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.deposit_model = cls.env["purchase.advance.payment.inv"]

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
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        # Check invoice plan created
        self.assertTrue(self.test_po_service.invoice_plan_ids)
        with self.assertRaises(UserError):
            self.test_po_service.invoice_plan_ids[1].invoice_type = "advance"
            self.test_po_service._check_invoice_plan_ids()
        # If advance percent is not filled, show error
        advance_line = self.test_po_service.invoice_plan_ids.filtered(
            lambda pln: pln.invoice_type == "advance"
        )
        self.assertEqual(len(advance_line), 1, "No one advance line")
        # Add 10% to advance
        advance_line.percent = 10
        # Confirm PO and create invoices
        self.test_po_service.button_confirm()
        self.assertEqual(self.test_po_service.state, "purchase")
        self.assertTrue(self.test_po_service.ip_invoice_plan)
        # Check there is deposit installment must register deposit first
        with self.assertRaises(UserError):
            self.test_po_service.action_create_invoice()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(**ctx).create_invoices_by_plan()
        # Valid number of invoices, including advance
        invoices = self.test_po_service.invoice_ids
        self.assertEqual(
            len(invoices), num_installment + 1, "Wrong number of invoice created"
        )
        # Validate advance amount, which is 10% of purhcase order
        adv_invoice = (
            invoices.mapped("invoice_line_ids")
            .filtered(
                lambda line: line.purchase_line_id.is_deposit and line.quantity == 1
            )
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
            .filtered(lambda line: line.product_id == self.test_service)
            .mapped("quantity")
        )
        self.assertEqual(quantity, 1, "Wrong number of total invoice quantity")

    def test_invoice_plan_with_multiple_advances(self):
        """Two advance lines with different plan_dates.
        to_invoice and default_get must follow (plan_date, id) order, not id alone."""
        self.test_service.purchase_method = "purchase"
        ctx = {
            "active_id": self.test_po_service.id,
            "active_ids": [self.test_po_service.id],
        }
        # Create plan: 3 installments + 2 advances via wizard
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 3
            p.advance = True
            p.num_advance = 2
            p.advance_percent = 10
        purchase_plan = p.save()
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        advance_lines = self.test_po_service.invoice_plan_ids.filtered(
            lambda pln: pln.invoice_type == "advance"
        )
        self.assertEqual(len(advance_lines), 2)
        # Change percent
        advance_lines.sorted("id")[0].write({"percent": 30, "plan_date": "2026-07-01"})
        advance_lines.sorted("id")[1].write({"percent": 20, "plan_date": "2026-06-01"})
        self.test_po_service.button_confirm()
        self.assertEqual(self.test_po_service.state, "purchase")
        # to_invoice must be on earlier plan_date advance (20%, 2026-06-01)
        adv_to_invoice = self.test_po_service.invoice_plan_ids.filtered(
            lambda pln: pln.invoice_type == "advance" and pln.to_invoice
        )
        self.assertEqual(len(adv_to_invoice), 1)
        self.assertEqual(adv_to_invoice.percent, 20)
        # default_get defaults to first-to-process advance (20%)
        defaults = self.deposit_model.with_context(**ctx).default_get(["amount"])
        self.assertAlmostEqual(defaults.get("amount", 0), 20)
        # Register first deposit (20%)
        deposit_wiz = self.deposit_model.with_context(**ctx).create(
            {"advance_payment_method": "percentage", "amount": 20}
        )
        deposit_wiz.with_context(**ctx).create_invoices()
        self.test_po_service.invoice_plan_ids.invalidate_recordset()
        # First invoice = 20% of PO amount_untaxed
        po_amount = self.test_po_service.amount_untaxed
        invoices = self.test_po_service.invoice_ids
        self.assertEqual(len(invoices), 1)
        self.assertAlmostEqual(invoices.amount_untaxed, po_amount * 0.20, places=2)
        self.assertTrue(self.test_po_service.need_advance)
        # to_invoice shifts to 30% advance
        adv_to_invoice2 = self.test_po_service.invoice_plan_ids.filtered(
            lambda pln: pln.invoice_type == "advance" and pln.to_invoice
        )
        self.assertEqual(len(adv_to_invoice2), 1)
        self.assertEqual(adv_to_invoice2.percent, 30)
        # default_get now returns 30%
        defaults2 = self.deposit_model.with_context(**ctx).default_get(["amount"])
        self.assertAlmostEqual(defaults2.get("amount", 0), 30)
        # Register second deposit (30%)
        deposit_wiz2 = self.deposit_model.with_context(**ctx).create(
            {"advance_payment_method": "percentage", "amount": 30}
        )
        deposit_wiz2.with_context(**ctx).create_invoices()
        self.test_po_service.invoice_plan_ids.invalidate_recordset()
        # Both deposits done: need_advance False, 2 invoices total
        self.assertFalse(self.test_po_service.need_advance)
        second_inv = self.test_po_service.invoice_ids - invoices
        self.assertEqual(len(self.test_po_service.invoice_ids), 2)
        self.assertAlmostEqual(second_inv.amount_untaxed, po_amount * 0.30, places=2)
