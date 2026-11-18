# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, new_test_user
from odoo.tools import mute_logger

from .common import TestPurchaseInvoicePlanCommon


class TestPurchaseInvoicePlanStandard(TestPurchaseInvoicePlanCommon):
    """Bills created by the standard flows follow the invoice plan"""

    def test_create_bills(self):
        """Create Bills of the purchase list bills the next installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        first, second = purchase.invoice_plan_ids[:2]
        bill = self._create_bills(purchase)
        line = bill.invoice_line_ids
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.balance, 2000)
        self.assertEqual(line.purchase_invoice_plan_id, first)
        self.assertEqual(bill.invoice_date, first.plan_date)
        self.assertEqual(first.invoice_ids, bill)
        self.assertTrue(first.invoiced)
        self.assertEqual(first.amount_invoiced, 2000)
        self.assertTrue(second.to_invoice)
        # Cancelled bill releases its installment
        bill.button_cancel()
        self.assertFalse(first.invoiced)
        self.assertTrue(first.to_invoice)
        bill = self._create_bills(purchase)
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, first)
        bill = self._create_bills(purchase)
        self.assertEqual(bill.invoice_line_ids.quantity, 2)
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, second)
        self.assertEqual(bill.invoice_date, second.plan_date)

    def test_create_bills_received_less(self):
        """Not more than the received quantity is billed"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 1)
        first = purchase.invoice_plan_ids[0]
        bill = self._create_bills(purchase)
        self.assertEqual(bill.invoice_line_ids.quantity, 1)
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, first)
        self.assertEqual(first.amount_invoiced, 1000)

    def test_create_bills_nothing_received(self):
        """A bill without quantity to bill does not use an installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        bill = self._create_bills(purchase)
        self.assertFalse(bill.invoice_line_ids.purchase_invoice_plan_id)
        self.assertFalse(bill.invoice_date)
        self.assertTrue(purchase.invoice_plan_ids[0].to_invoice)

    def test_create_bills_refund(self):
        """A bill switched to refund does not use an installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        first = purchase.invoice_plan_ids[0]
        bill = self._create_bills(purchase)
        self.assertTrue(first.invoiced)
        bill.action_switch_move_type()
        self.assertEqual(bill.move_type, "in_refund")
        self.assertFalse(bill.invoice_line_ids.purchase_invoice_plan_id)
        self.assertFalse(first.invoice_ids)
        self.assertFalse(first.invoiced)
        self.assertTrue(first.to_invoice)
        # Switched back to bill, it bills the installment again
        bill.action_switch_move_type()
        self.assertEqual(bill.move_type, "in_invoice")
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, first)
        self.assertTrue(first.invoiced)

    def test_bill_quantity_zero(self):
        """Bill line edited to zero quantity releases its installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        first = purchase.invoice_plan_ids[0]
        bill = self._create_bills(purchase)
        bill.invoice_line_ids.quantity = 0
        self.assertFalse(bill.invoice_line_ids.purchase_invoice_plan_id)
        self.assertFalse(bill.purchase_invoice_plan_ids)
        self.assertFalse(first.invoiced)
        bill.invoice_line_ids.quantity = 2
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, first)
        self.assertEqual(bill.purchase_invoice_plan_ids, first)

    def test_create_bills_multi_purchase(self):
        """One bill for 2 orders bills the next installment of each order"""
        purchase = self.test_po_product
        purchase2 = self._create_purchase_order(self.test_product, 4, 500)
        self._create_invoice_plan(purchase, 5)
        self._create_invoice_plan(purchase2, 2)
        (purchase | purchase2).button_confirm()
        self._receive(purchase, 10)
        self._receive(purchase2, 4)
        bill = self._create_bills(purchase | purchase2)
        self.assertEqual((purchase | purchase2).invoice_ids, bill)
        line = bill.invoice_line_ids.filtered(
            lambda ln: ln.purchase_order_id == purchase
        )
        line2 = bill.invoice_line_ids.filtered(
            lambda ln: ln.purchase_order_id == purchase2
        )
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.purchase_invoice_plan_id, purchase.invoice_plan_ids[0])
        self.assertEqual(line2.quantity, 2)
        self.assertEqual(line2.purchase_invoice_plan_id, purchase2.invoice_plan_ids[0])
        self.assertEqual(purchase.invoice_plan_ids[0].amount_invoiced, 2000)
        self.assertEqual(purchase2.invoice_plan_ids[0].amount_invoiced, 1000)
        self.assertEqual(
            bill.purchase_invoice_plan_ids,
            purchase.invoice_plan_ids[0] | purchase2.invoice_plan_ids[0],
        )

    def test_vendor_bill_auto_complete(self):
        """Vendor bill completed from the purchase order bills next installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        with mute_logger("odoo.tests.form.onchange"):
            move_form.purchase_vendor_bill_id = self.env["purchase.bill.union"].browse(
                -purchase.id
            )
        self.assertEqual(
            move_form.purchase_invoice_plan_ids[:], purchase.invoice_plan_ids[0]
        )
        bill = move_form.save()
        line = bill.invoice_line_ids
        first, second = purchase.invoice_plan_ids[:2]
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.purchase_invoice_plan_id, first)
        self.assertEqual(first.invoice_ids, bill)
        self.assertEqual(bill.invoice_date, first.plan_date)
        # Date of the vendor bill entered before the auto-complete is kept
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form.partner_id = self.test_partner
        move_form.invoice_date = fields.Date.to_date("2026-01-15")
        with mute_logger("odoo.tests.form.onchange"):
            move_form.purchase_vendor_bill_id = self.env["purchase.bill.union"].browse(
                -purchase.id
            )
        bill = move_form.save()
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, second)
        self.assertEqual(bill.invoice_date, fields.Date.to_date("2026-01-15"))

    def test_edi_import(self):
        """Bill imported from a vendor document keeps the quantity of the
        document matching and is linked to the next installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        bill = self.env["account.move"].create(
            {"move_type": "in_invoice", "partner_id": self.test_partner.id}
        )
        bill._set_purchase_orders(purchase)
        line = bill.invoice_line_ids.filtered(lambda ln: ln.display_type == "product")
        self.assertEqual(line.quantity, 10)
        self.assertEqual(line.purchase_invoice_plan_id, purchase.invoice_plan_ids[0])
        self.assertFalse(bill.invoice_date)

    def test_bill_matching(self):
        """Vendor bill matched with the purchase order keeps the vendor
        quantity, by an accountant without purchase rights"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        accountant = new_test_user(
            self.env,
            login="test_accountant",
            groups="account.group_account_invoice",
        )
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.test_partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.test_product.id,
                            "quantity": 3,
                            "price_unit": 1000,
                            "tax_ids": False,
                        }
                    )
                ],
            }
        )
        line = bill.invoice_line_ids
        self.assertFalse(line.purchase_invoice_plan_id)
        match_lines = (
            self.env["purchase.bill.line.match"]
            .with_user(accountant)
            .search([("partner_id", "=", self.test_partner.id)])
        )
        match_lines.action_match_lines()
        self.assertEqual(line.purchase_line_id, purchase.order_line)
        self.assertEqual(line.quantity, 3)
        self.assertFalse(bill.invoice_date)
        first = purchase.invoice_plan_ids[0]
        self.assertEqual(line.purchase_invoice_plan_id, first)
        self.assertEqual(first.amount_invoiced, 3000)
        # The accountant reads the installments of the order
        plans = purchase.invoice_plan_ids.with_user(accountant)
        self.assertEqual(plans[0].amount, 3000)
        self.assertEqual(plans[0].percent, 30)
        # Unmatched line releases its installment
        line.purchase_line_id = False
        self.assertFalse(line.purchase_invoice_plan_id)
        self.assertFalse(first.invoiced)

    def test_bill_matching_create_bill(self):
        """Bill created from purchase order lines in Bill Matching works as
        Create Bills"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        match_lines = self.env["purchase.bill.line.match"].search(
            [("purchase_order_id", "=", purchase.id)]
        )
        action = match_lines.action_match_lines()
        bill = self.env["account.move"].browse(action["res_id"])
        first = purchase.invoice_plan_ids[0]
        self.assertEqual(bill.invoice_line_ids.quantity, 2)
        self.assertEqual(bill.invoice_line_ids.purchase_invoice_plan_id, first)
        self.assertEqual(bill.invoice_date, first.plan_date)

    def test_create_bills_after_return(self):
        """Returned products are credited by the standard refund, not billed
        by the next installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        self._create_bills(purchase).sudo().action_post()
        self._create_bills(purchase).sudo().action_post()
        receipt = purchase.picking_ids
        returned = receipt._create_return()
        returned.move_ids.product_uom_qty = 8
        returned.action_confirm()
        returned.move_ids.quantity = 8
        returned.move_ids.picked = True
        returned.button_validate()
        self.assertEqual(purchase.order_line.qty_to_invoice, -2)
        third = purchase.invoice_plan_ids[2]
        with self.assertRaises(ValidationError):
            self._create_bill_by_plan(purchase)
        refund = self._create_bills(purchase)
        self.assertEqual(refund.move_type, "in_refund")
        self.assertEqual(refund.invoice_line_ids.quantity, 2)
        self.assertFalse(refund.invoice_line_ids.purchase_invoice_plan_id)
        self.assertTrue(third.to_invoice)

    def test_bill_line_installment_check(self):
        """A bill bills one installment of its purchase order"""
        purchase = self.test_po_product
        purchase.order_line = [
            Command.create(
                {
                    "product_id": self.test_service.id,
                    "product_qty": 1,
                    "price_unit": 500,
                    "tax_ids": False,
                }
            )
        ]
        self._create_invoice_plan(purchase, 5)
        other = self._create_plan_purchase()
        (purchase | other).button_confirm()
        self._receive(purchase, 10)
        bill = self._create_bills(purchase)
        lines = bill.invoice_line_ids
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines.purchase_invoice_plan_id, purchase.invoice_plan_ids[0])
        with self.assertRaises(ValidationError):
            lines[0].purchase_invoice_plan_id = purchase.invoice_plan_ids[1]
        with self.assertRaises(ValidationError):
            lines.purchase_invoice_plan_id = other.invoice_plan_ids[0]
        lines.purchase_invoice_plan_id = purchase.invoice_plan_ids[1]
        self.assertEqual(bill.purchase_invoice_plan_ids, purchase.invoice_plan_ids[1])
