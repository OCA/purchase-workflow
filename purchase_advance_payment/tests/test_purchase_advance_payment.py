# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)


from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestPurchaseAdvancePayment(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})
        cls.res_partner_address_1 = cls.env["res.partner"].create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Partner 12"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "type": "consu", "purchase_method": "purchase"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "type": "consu", "purchase_method": "purchase"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Repair Services",
                "type": "service",
                "purchase_method": "purchase",
            }
        )

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 20",
                "type_tax_use": "purchase",
                "amount": 20,
            }
        )

        # purchase Order
        cls.purchase_order_1 = cls.env["purchase.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        cls.order_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 10.0,
                "price_unit": 100.0,
                "taxes_id": cls.tax,
            }
        )
        cls.order_line_2 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_qty": 25.0,
                "price_unit": 40.0,
                "taxes_id": cls.tax,
            }
        )
        cls.order_line_3 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_qty": 20.0,
                "price_unit": 50.0,
                "taxes_id": cls.tax,
            }
        )

        cls.currency_euro = cls.env["res.currency"].search([("name", "=", "EUR")])
        cls.currency_usd = cls.env["res.currency"].search([("name", "=", "USD")])
        cls.currency_rate = cls.env["res.currency.rate"].create(
            {
                "rate": 1.20,
                "currency_id": cls.currency_usd.id,
            }
        )

        cls.journal_eur_bank = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Bank",
                "type": "bank",
                "code": "111",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_bank = cls.env["account.journal"].create(
            {
                "name": "Journal USD Bank",
                "type": "bank",
                "code": "222",
                "currency_id": cls.currency_usd.id,
            }
        )
        cls.journal_eur_cash = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Cash",
                "type": "cash",
                "code": "333",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_cash = cls.env["account.journal"].create(
            {
                "name": "Journal USD Cash",
                "type": "cash",
                "code": "444",
                "currency_id": cls.currency_usd.id,
            }
        )

    def test_01_purchase_advance_payment(self):
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
            "Amounts should match",
        )

        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }

        # Check residual > advance payment and the comparison takes
        # into account the currency. 3001*1.2 > 3600
        with self.assertRaises(ValidationError):
            advance_payment_0 = (
                self.env["account.voucher.wizard.purchase"]
                .with_context(context_payment)
                .create(
                    {
                        "journal_id": self.journal_eur_bank.id,
                        "amount_advance": 3001,
                        "order_id": self.purchase_order_1.id,
                    }
                )
            )
            advance_payment_0.make_advance_payment()

        # Create Advance Payment 1 - EUR - bank
        advance_payment_1 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "amount_advance": 100,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_1.make_advance_payment()

        self.assertEqual(self.purchase_order_1.amount_residual, 3480)

        # Create Advance Payment 2 - USD - cash
        advance_payment_2 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()

        self.assertEqual(self.purchase_order_1.amount_residual, 3280)

        # Confirm Purchase Order
        self.purchase_order_1.button_confirm()

        # Create Advance Payment 3 - EUR - cash
        advance_payment_3 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_cash.id,
                    "amount_advance": 250,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_3.make_advance_payment()
        self.assertEqual(self.purchase_order_1.amount_residual, 2980)

        # Create Advance Payment 4 - USD - bank
        advance_payment_4 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_bank.id,
                    "amount_advance": 400,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_4.make_advance_payment()
        self.assertEqual(self.purchase_order_1.amount_residual, 2580)

    def test_02_residual_amount_with_bill(self):
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )
        # Create Advance Payment 1 - EUR - bank
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment 2 - USD - cash
        advance_payment_2 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()
        pre_payment = self.purchase_order_1.account_payment_ids
        self.assertEqual(len(pre_payment), 1)
        self.assertEqual(self.purchase_order_1.amount_residual, 3400)
        # generate bill, pay bill, check amount residual.
        self.purchase_order_1.button_confirm()
        self.assertEqual(self.purchase_order_1.invoice_status, "to invoice")
        self.purchase_order_1.action_create_invoice()
        self.assertEqual(self.purchase_order_1.invoice_status, "invoiced")
        self.assertEqual(self.purchase_order_1.amount_residual, 3400)
        invoice = self.purchase_order_1.invoice_ids
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        active_ids = invoice.ids
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=active_ids
        ).create(
            {
                "amount": 1200.0,
                "group_payment": True,
                "payment_difference_handling": "open",
            }
        )._create_payments()
        self.assertEqual(self.purchase_order_1.amount_residual, 2200)

        # Reconciling the pre-payment should not affect amount_residual in PO.
        (
            liquidity_lines,
            counterpart_lines,
            writeoff_lines,
        ) = pre_payment._seek_for_lines()
        (
            counterpart_lines
            + invoice.line_ids.filtered(
                lambda line: line.account_internal_type == "payable"
            )
        ).reconcile()
        self.purchase_order_1.invalidate_cache()
        self.assertEqual(self.purchase_order_1.amount_residual, 2200)

    def test_03_residual_amount_big_pre_payment(self):
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )
        # Create Advance Payment 1 - EUR - bank
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment 2 - USD - cash
        advance_payment_2 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 2000,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()
        pre_payment = self.purchase_order_1.account_payment_ids
        self.assertEqual(len(pre_payment), 1)
        self.assertEqual(self.purchase_order_1.amount_residual, 1600)
        # generate a partial bill, reconcile with pre payment, check amount residual.
        self.purchase_order_1.button_confirm()
        self.assertEqual(self.purchase_order_1.invoice_status, "to invoice")
        # Adjust billing method to then do a partial bill with a total amount
        # smaller than the pre-payment.
        self.product_1.purchase_method = "receive"
        self.order_line_1.qty_received = 10.0
        self.assertEqual(self.order_line_1.qty_to_invoice, 10.0)
        self.product_2.purchase_method = "receive"
        self.order_line_2.qty_received = 0.0
        self.assertEqual(self.order_line_2.qty_to_invoice, 0.0)
        self.product_3.purchase_method = "receive"
        self.order_line_3.qty_received = 0.0
        self.assertEqual(self.order_line_3.qty_to_invoice, 0.0)
        self.purchase_order_1.action_create_invoice()
        self.assertEqual(self.purchase_order_1.invoice_status, "invoiced")
        self.assertEqual(self.purchase_order_1.amount_residual, 1600)
        invoice = self.purchase_order_1.invoice_ids
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        self.assertEqual(invoice.amount_residual, 1200)
        active_ids = invoice.ids
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=active_ids
        ).create(
            {
                "amount": 300.0,
                "group_payment": True,
                "payment_difference_handling": "open",
            }
        )._create_payments()
        self.assertEqual(invoice.amount_residual, 900)
        self.assertEqual(self.purchase_order_1.amount_residual, 1300)

        # Partially reconciling the pre-payment should not affect amount_residual in PO.
        (
            liquidity_lines,
            counterpart_lines,
            writeoff_lines,
        ) = pre_payment._seek_for_lines()
        (
            counterpart_lines
            + invoice.line_ids.filtered(
                lambda line: line.account_internal_type == "payable"
            )
        ).reconcile()
        self.purchase_order_1.invalidate_cache()
        self.assertEqual(self.purchase_order_1.amount_residual, 1300)
