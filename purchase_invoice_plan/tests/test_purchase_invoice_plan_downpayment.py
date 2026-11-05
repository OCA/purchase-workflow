# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command

from .common import TestPurchaseInvoicePlanCommon


class TestPurchaseInvoicePlanDownpayment(TestPurchaseInvoicePlanCommon):
    """Down payments of the standard are deducted in proportion of each
    installment, the last installment deducts the remaining"""

    def _add_downpayment(self, purchase, amount, product=None):
        """Vendor bill of a down payment, added to the purchase order with
        Bill Matching > Add to PO > Add Down Payment"""
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.test_partner.id,
                "invoice_date": "2026-10-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Deposit",
                            "product_id": product and product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "tax_ids": False,
                        }
                    )
                ],
            }
        )
        bill.sudo().action_post()
        self.env["bill.to.po.wizard"].with_context(
            active_ids=[-bill.invoice_line_ids.id]
        ).create({"purchase_order_id": purchase.id}).action_add_downpayment()
        return bill

    def _deduction(self, bill):
        return bill.invoice_line_ids.filtered(
            lambda ln: ln.is_downpayment and ln.display_type == "product"
        )

    def test_create_bill_by_plan(self):
        """Down payment lower than the installment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        down_payment = self._add_downpayment(purchase, 1000, self.test_service)
        self._receive(purchase, 10)
        self._create_bill_by_plan(purchase)
        bill = purchase.invoice_ids - down_payment
        first = purchase.invoice_plan_ids[0]
        self.assertEqual(bill.move_type, "in_invoice")
        self.assertEqual(self._deduction(bill).quantity, -0.2)
        self.assertEqual(bill.amount_untaxed, 1800)
        self.assertEqual(bill.purchase_invoice_plan_ids, first)
        self.assertFalse(self._deduction(bill).purchase_invoice_plan_id)
        # Installment amount is before the deduction
        self.assertEqual(first.amount_invoiced, 2000)

    def test_create_bills_more_than_installment(self):
        """Down payment higher than the installment does not make a refund"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._add_downpayment(purchase, 3000)
        self._receive(purchase, 10)
        bill = self._create_bills(purchase)
        self.assertEqual(bill.move_type, "in_invoice")
        self.assertEqual(self._deduction(bill).quantity, -0.2)
        self.assertEqual(bill.amount_untaxed, 1400)
        self.assertTrue(purchase.invoice_plan_ids[0].invoiced)

    def test_all_installments(self):
        """All installments deduct the whole down payment"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        down_payment = self._add_downpayment(purchase, 3000, self.test_service)
        self._receive(purchase, 10)
        self._create_bill_by_plan(purchase, all_remain=True)
        bills = purchase.invoice_ids - down_payment
        self.assertEqual(len(bills), 5)
        self.assertEqual(set(bills.mapped("move_type")), {"in_invoice"})
        self.assertEqual(set(bills.mapped("amount_untaxed")), {1400})
        self.assertEqual(sum(self._deduction(bills).mapped("quantity")), -1)
        self.assertTrue(all(purchase.invoice_plan_ids.mapped("invoiced")))

    def test_create_bills_received_less(self):
        """Partial bill of an installment deducts in proportion of the bill"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._add_downpayment(purchase, 3000)
        self._receive(purchase, 1)
        bill = self._create_bills(purchase)
        self.assertEqual(self._deduction(bill).quantity, -0.1)
        self.assertEqual(bill.amount_untaxed, 700)

    def test_downpayment_after_bill(self):
        """Down payment added after a bill is deducted by the next
        installments, the last one deducts the remaining"""
        purchase = self.test_po_product
        self._create_invoice_plan(purchase, 5)
        purchase.button_confirm()
        self._receive(purchase, 10)
        self._create_bill_by_plan(purchase)
        down_payment = self._add_downpayment(purchase, 3000, self.test_service)
        self._create_bill_by_plan(purchase)
        second = purchase.invoice_plan_ids[1].invoice_ids
        self.assertEqual(self._deduction(second).quantity, -0.2)
        self._create_bill_by_plan(purchase, all_remain=True)
        bills = purchase.invoice_ids - down_payment
        last = purchase.invoice_plan_ids[-1].invoice_ids
        self.assertEqual(len(bills), 5)
        self.assertEqual(self._deduction(last).quantity, -0.4)
        self.assertEqual(sum(self._deduction(bills).mapped("quantity")), -1)
