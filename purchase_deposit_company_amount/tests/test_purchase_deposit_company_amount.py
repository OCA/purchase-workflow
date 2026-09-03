# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseDepositCompanyAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "test company",
                "currency_id": cls.env.ref("base.JPY").id,
                "country_id": cls.env.ref("base.jp").id,
            }
        )
        cls.env.user.company_id = cls.company
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_usd.active = True
        Rate = cls.env["res.currency.rate"]
        Rate.create(
            {
                "name": "2025-10-01",
                "currency_id": cls.currency_usd.id,
                "company_id": cls.company.id,
                "rate": 1 / 150.0,
            }
        )
        Rate.create(
            {
                "name": "2025-11-01",
                "currency_id": cls.currency_usd.id,
                "company_id": cls.company.id,
                "rate": 1 / 160.0,
            }
        )
        Account = cls.env["account.account"]
        account_payable = Account.create(
            {
                "code": "TEST1",
                "name": "Payable",
                "reconcile": True,
                "account_type": "liability_payable",
                "company_id": cls.company.id,
            }
        )
        account_expense = Account.create(
            {
                "code": "TEST2",
                "name": "Expense",
                "account_type": "expense",
                "company_id": cls.company.id,
            }
        )
        stock_valuation = Account.create(
            {
                "code": "TEST3",
                "name": "Stock Valuation",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        stock_input = Account.create(
            {
                "code": "TEST4",
                "name": "Stock Input",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        stock_output = Account.create(
            {
                "code": "TEST5",
                "name": "Stock Output",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "test partner",
                "property_account_payable_id": account_payable.id,
                "company_id": cls.company.id,
            }
        )
        stock_journal = cls.env["account.journal"].create(
            {
                "code": "Valuation",
                "name": "Valuation Journal",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.category = cls.env["product.category"].create(
            {
                "name": "Deposit Test Category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_account_expense_categ_id": account_expense.id,
                "property_stock_valuation_account_id": stock_valuation.id,
                "property_stock_account_input_categ_id": stock_input.id,
                "property_stock_account_output_categ_id": stock_output.id,
                "property_stock_journal": stock_journal.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Deposit Test Product",
                "type": "product",
                "categ_id": cls.category.id,
                "company_id": cls.company.id,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Deposit Test Product B",
                "type": "product",
                "categ_id": cls.category.id,
                "company_id": cls.company.id,
            }
        )
        cls.product_c = cls.env["product.product"].create(
            {
                "name": "Deposit Test Product C",
                "type": "product",
                "categ_id": cls.category.id,
                "company_id": cls.company.id,
            }
        )
        cls.account_deposit = Account.create(
            {
                "name": "Purchase Deposit",
                "code": "TEST6",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "code": "TP",
                "name": "Test Purchase",
                "type": "purchase",
                "company_id": cls.company.id,
            }
        )

    DEPOSIT_DATE = "2025-10-01"
    FINAL_DATE = "2025-11-01"

    def _create_purchase_order(self, lines=None, currency=None):
        lines = lines or [(self.product, 100.0)]
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "date_order": fields.Date.from_string(self.DEPOSIT_DATE),
                "company_id": self.company.id,
                "currency_id": (currency or self.currency_usd).id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_qty": 1.0,
                            "price_unit": price,
                        }
                    )
                    for product, price in lines
                ],
            }
        )
        po.button_confirm()
        return po

    def _register_deposit(self, po, percentage=30):
        wizard_env = self.env["purchase.advance.payment.inv"].with_context(
            active_id=po.id,
            active_ids=po.ids,
            active_model="purchase.order",
            create_bills=True,
        )
        with Form(wizard_env) as advance_form:
            advance_form.advance_payment_method = "percentage"
            advance_form.amount = percentage
            advance_form.deposit_account_id = self.account_deposit
        advance_form.save().create_invoices()
        deposit_bill = po.invoice_ids
        deposit_bill.invoice_date = fields.Date.from_string(self.DEPOSIT_DATE)
        return deposit_bill

    def _post_deposit_bill(self, po, company_amount, percentage=30):
        deposit_bill = self._register_deposit(po, percentage)
        self._deposit_line(deposit_bill).company_amount = company_amount
        deposit_bill.action_post()
        return deposit_bill

    def _create_final_bill(self, po, receive=True):
        if receive:
            po.picking_ids.move_ids.write({"quantity_done": 1})
            po.picking_ids.button_validate()
        existing = po.invoice_ids
        po.with_context(create_bill=True).action_create_invoice()
        bill = po.invoice_ids - existing
        bill.invoice_date = fields.Date.from_string(self.FINAL_DATE)
        return bill

    def _create_bill_without_deposit(self):
        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "currency_id": self.currency_usd.id,
                "invoice_date": fields.Date.from_string(self.FINAL_DATE),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def _deposit_po_line(self, po):
        return po.order_line.filtered(lambda l: l.is_deposit and not l.display_type)

    def _deposit_line(self, move):
        return move.line_ids.filtered(
            lambda l: l.purchase_line_id.is_deposit and l.quantity > 0
        )

    def _offset_line(self, move):
        return move.line_ids.filtered(
            lambda l: l.purchase_line_id.is_deposit and l.quantity < 0
        )

    def _goods_lines(self, move):
        return move.line_ids.filtered(
            lambda l: l.display_type == "product" and not l.purchase_line_id.is_deposit
        )

    def _goods_line(self, move, product):
        return self._goods_lines(move).filtered(lambda l: l.product_id == product)

    def _payable_line(self, move):
        return move.line_ids.filtered(
            lambda l: l.account_id.account_type == "liability_payable"
        )

    def test_deposit_rate_difference_lands_on_the_goods(self):
        po = self._create_purchase_order()
        self._post_deposit_bill(po, 3900)
        self.assertEqual(self._deposit_po_line(po).deposit_company_amount, 3900)
        bill = self._create_final_bill(po)
        goods_line = self._goods_lines(bill)
        self.assertEqual(self._offset_line(bill).balance, -3900)
        self.assertEqual(goods_line.balance, 15100)
        self.assertEqual(self._payable_line(bill).balance, -11200)
        self.assertFalse(goods_line.company_amount)
        self.assertAlmostEqual(
            goods_line._get_gross_unit_price()
            / goods_line.currency_rate
            * goods_line.quantity,
            goods_line.balance,
            places=2,
        )
        self.assertNotAlmostEqual(
            goods_line.balance, goods_line._get_rate_based_balance(), places=2
        )
        bill.action_post()
        self.assertEqual(self._offset_line(bill).balance, -3900)
        self.assertEqual(goods_line.balance, 15100)
        self.assertEqual(self._payable_line(bill).balance, -11200)
        self.assertEqual(
            sum(bill.line_ids.mapped("stock_valuation_layer_ids").mapped("value")),
            -900.0,
        )

    def test_rate_difference_is_prorated_across_goods_lines(self):
        po = self._create_purchase_order(
            [(self.product, 20.0), (self.product_b, 30.0), (self.product_c, 50.0)]
        )
        self._post_deposit_bill(po, 3801)
        bill = self._create_final_bill(po)
        line_a = self._goods_line(bill, self.product)
        line_b = self._goods_line(bill, self.product_b)
        line_c = self._goods_line(bill, self.product_c)
        self.assertEqual(line_a.balance, 3000)
        self.assertEqual(line_b.balance, 4500)
        self.assertEqual(line_c.balance, 7501)
        self.assertEqual(self._offset_line(bill).balance, -3801)
        self.assertEqual(line_a.balance + line_b.balance + line_c.balance - 16000, -999)
        self.assertEqual(self._payable_line(bill).balance, -11200)
        bill.action_post()
        self.assertEqual(
            sum(bill.line_ids.mapped("stock_valuation_layer_ids").mapped("value")),
            -999.0,
        )

    def test_deposit_value_is_read_back_from_the_ledger(self):
        po = self._create_purchase_order()
        deposit_bill = self._post_deposit_bill(po, 3900)
        deposit_po_line = self._deposit_po_line(po)
        self.assertEqual(deposit_po_line.deposit_company_amount, 3900)
        deposit_bill.button_draft()
        self.assertEqual(deposit_po_line.deposit_company_amount, 0)

    def test_only_the_deposit_bill_may_be_pinned(self):
        po = self._create_purchase_order()
        deposit_bill = self._post_deposit_bill(po, 3900)
        self.assertTrue(deposit_bill.is_deposit)
        bill = self._create_final_bill(po)
        self.assertFalse(bill.is_deposit)
        self.assertTrue(bill._get_deposit_offset_lines())
        with self.assertRaises(ValidationError):
            self._goods_lines(bill).company_amount = 17000
        with self.assertRaises(ValidationError):
            self._offset_line(bill).company_amount = 3000

    def test_company_currency_deposit_bill_refuses_the_override(self):
        po = self._create_purchase_order(currency=self.company.currency_id)
        deposit_bill = self._register_deposit(po)
        self.assertTrue(deposit_bill.is_deposit)
        self.assertFalse(deposit_bill.allow_company_amount)
        with self.assertRaises(ValidationError):
            self._deposit_line(deposit_bill).company_amount = 3900

    def test_switching_the_bill_to_the_company_currency_is_rejected(self):
        po = self._create_purchase_order()
        deposit_bill = self._register_deposit(po)
        self._deposit_line(deposit_bill).company_amount = 3900
        with self.assertRaises(ValidationError):
            deposit_bill.currency_id = self.company.currency_id

    def test_unpinned_deposit_keeps_the_standard_conversion(self):
        po = self._create_purchase_order()
        deposit_bill = self._register_deposit(po)
        deposit_bill.action_post()
        deposit_po_line = self._deposit_po_line(po)
        self.assertEqual(deposit_po_line.deposit_company_amount, 0)
        self.assertEqual(self._deposit_line(deposit_bill).balance, 4500)
        bill = self._create_final_bill(po)
        self.assertEqual(self._offset_line(bill).balance, -4800)
        self.assertEqual(self._goods_lines(bill).balance, 16000)
        self.assertEqual(self._payable_line(bill).balance, -11200)

    def test_clearing_the_pinned_amount_restores_the_conversion(self):
        po = self._create_purchase_order()
        deposit_bill = self._register_deposit(po)
        deposit_line = self._deposit_line(deposit_bill)
        deposit_line.company_amount = 3900
        self.assertEqual(deposit_line.balance, 3900)
        self.assertEqual(self._payable_line(deposit_bill).balance, -3900)
        deposit_line.company_amount = 0
        self.assertEqual(deposit_line.balance, 4500)
        self.assertEqual(self._payable_line(deposit_bill).balance, -4500)
        deposit_bill.action_post()
        self.assertEqual(self._deposit_po_line(po).deposit_company_amount, 0)

    def test_posted_moves_are_not_re_booked(self):
        po = self._create_purchase_order()
        self._post_deposit_bill(po, 3900)
        bill = self._create_final_bill(po)
        bill.action_post()
        before = {line: line.balance for line in bill.line_ids}
        rate = self.env["res.currency.rate"].search(
            [
                ("name", "=", self.FINAL_DATE),
                ("currency_id", "=", self.currency_usd.id),
                ("company_id", "=", self.company.id),
            ]
        )
        rate.rate = 1 / 155.0
        bill.invalidate_recordset()
        bill.line_ids.write({"name": "touched"})
        for line, balance in before.items():
            self.assertEqual(line.balance, balance)

    def test_plain_vendor_bill_is_untouched(self):
        bill = self._create_bill_without_deposit()
        line = bill.invoice_line_ids
        self.assertFalse(bill.is_deposit)
        self.assertEqual(line.balance, 16000)
        with self.assertRaises(ValidationError):
            line.company_amount = 17000

    def test_credit_note_reverses_the_final_bill(self):
        po = self._create_purchase_order()
        self._post_deposit_bill(po, 3900)
        bill = self._create_final_bill(po)
        bill.action_post()
        refund = bill._reverse_moves()
        refund.invoice_date = fields.Date.from_string(self.FINAL_DATE)
        self.assertEqual(refund.move_type, "in_refund")
        self.assertTrue(refund._get_deposit_offset_lines())
        self.assertEqual(self._offset_line(refund).balance, 3900)
        self.assertEqual(self._goods_lines(refund).balance, -15100)
        self.assertEqual(self._payable_line(refund).balance, 11200)
        refund.action_post()
        self.assertEqual(self._offset_line(refund).balance, 3900)
        self.assertEqual(self._goods_lines(refund).balance, -15100)
        pair = bill + refund
        for account in pair.line_ids.account_id:
            self.assertEqual(
                sum(
                    pair.line_ids.filtered(lambda l: l.account_id == account).mapped(
                        "balance"
                    )
                ),
                0,
                "%s does not net to zero across the bill and its reversal"
                % account.display_name,
            )

    def test_credit_note_and_rebill_leave_no_residue(self):
        po = self._create_purchase_order()
        self._post_deposit_bill(po, 3900)
        bill = self._create_final_bill(po)
        bill.action_post()
        refund = bill._reverse_moves()
        refund.invoice_date = fields.Date.from_string(self.FINAL_DATE)
        refund.action_post()
        deposit_line = self._deposit_po_line(po)
        self.assertEqual(deposit_line.deposit_company_amount, 3900)
        rebill = self._create_final_bill(po, receive=False)
        rebill.action_post()
        self.assertEqual(self._offset_line(rebill).balance, -3900)
        self.assertEqual(self._goods_lines(rebill).balance, 15100)
        posted = bill + refund + rebill
        self.assertEqual(
            sum(
                posted.line_ids.filtered(
                    lambda l: l.account_id == self.account_deposit
                ).mapped("balance")
            ),
            -3900,
        )
        self.assertEqual(sum(self._goods_lines(posted).mapped("balance")), 15100)

    def test_changing_the_bill_date_rebalances_the_deposit_bill(self):
        po = self._create_purchase_order()
        deposit_bill = self._register_deposit(po)
        deposit_bill.invoice_date = fields.Date.from_string(self.FINAL_DATE)
        deposit_line = self._deposit_line(deposit_bill)
        deposit_line.company_amount = 3900
        self.assertEqual(deposit_line.balance, 3900)
        deposit_bill.invoice_date = fields.Date.from_string(self.DEPOSIT_DATE)
        self.assertEqual(deposit_line.balance, 3900)
        self.assertEqual(self._payable_line(deposit_bill).balance, -3900)
        deposit_bill.action_post()

    def test_changing_the_bill_date_on_the_final_bill(self):
        po = self._create_purchase_order()
        self._post_deposit_bill(po, 3900)
        bill = self._create_final_bill(po)
        bill.invoice_date = fields.Date.from_string(self.DEPOSIT_DATE)
        self.assertEqual(self._offset_line(bill).balance, -3900)
        self.assertEqual(self._goods_lines(bill).balance, 14400)
        self.assertEqual(self._payable_line(bill).balance, -10500)
        bill.action_post()
