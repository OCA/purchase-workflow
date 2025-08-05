# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)


from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestPurchaseAdvancePayment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

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
        cls.purchase_order_2 = cls.env["purchase.order"].create(
            {"partner_id": cls.res_partner_2.id}
        )

        cls.order_line_2_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_2.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 10.0,
                "price_unit": 100.0,
                "taxes_id": cls.tax,
            }
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

        cls.active_euro = False
        cls.currency_euro = (
            cls.env["res.currency"]
            .with_context(active_test=False)
            .search([("name", "=", "EUR")])
        )
        # active euro currency if inactive for test
        if not cls.currency_euro.active:
            cls.currency_euro.active = True
            cls.active_euro = True
        cls.currency_usd = cls.env["res.currency"].search([("name", "=", "USD")])
        cls.currency_rate = cls.env["res.currency.rate"].create(
            {
                "inverse_company_rate": 1.20,
                "currency_id": cls.currency_euro.id,
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
        cls.env["ir.config_parameter"].sudo().set_param(
            "purchase_advance_payment.auto_reconcile_advance_payments", False
        )

    def test_00_with_context_payment(self):
        context_payment_2 = {
            "active_ids": [self.purchase_order_2.id],
            "active_id": self.purchase_order_2.id,
        }
        advance_payment_with_context = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment_2)
            .create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "amount_advance": 10,
                }
            )
        )
        self.assertEqual(advance_payment_with_context.order_id, self.purchase_order_2)

        advance_payment_without_context = self.env[
            "account.voucher.wizard.purchase"
        ].create(
            {
                "journal_id": self.journal_eur_bank.id,
                "amount_advance": 20,
                "order_id": self.purchase_order_1.id,
            }
        )
        self.assertEqual(
            advance_payment_without_context.order_id, self.purchase_order_1
        )

    def test_01_purchase_advance_payment(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )

        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }

        # Create Advance Payment 1 - EUR - bank
        advance_payment_1 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
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
            .with_context(**context_payment)
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
            .with_context(**context_payment)
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
            .with_context(**context_payment)
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
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
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
            .with_context(**context_payment)
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
                lambda line: line.account_type == "liability_payable"
            )
        ).reconcile()
        self.purchase_order_1.env.invalidate_all()
        self.assertEqual(self.purchase_order_1.amount_residual, 2200)

    def test_03_residual_amount_big_pre_payment(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
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
            .with_context(**context_payment)
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
                lambda line: line.account_type == "liability_payable"
            )
        ).reconcile()
        self.purchase_order_1.env.invalidate_all()
        self.assertEqual(self.purchase_order_1.amount_residual, 1300)

    def test_04_residual_amount_with_no_amount_left(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment with the same residual amount
        advance_payment = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 3600,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment.make_advance_payment()
        self.assertEqual(self.purchase_order_1.amount_residual, 0)
        self.assertEqual(self.purchase_order_1.advance_payment_status, "paid")

    def test_05_check_residual_amount_warning(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
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
        mes = "Amount of advance is greater than residual amount on purchase"
        with self.assertRaisesRegex(ValidationError, mes):
            advance_payment_0 = (
                self.env["account.voucher.wizard.purchase"]
                .with_context(**context_payment)
                .create(
                    {
                        "journal_id": self.journal_eur_bank.id,
                        "amount_advance": 3001,
                        "order_id": self.purchase_order_1.id,
                    }
                )
            )
            advance_payment_0.make_advance_payment()
        # Check positive advance payment
        mes2 = "Amount of advance must be positive."
        with self.assertRaisesRegex(ValidationError, mes2):
            self.env["account.voucher.wizard.purchase"].create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "amount_advance": -300,
                    "order_id": self.purchase_order_2.id,
                }
            )

    def test_06_skip_payment_post(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment 1
        advance_payment_1 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "amount_advance": 100,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_1.make_advance_payment()
        payment_1 = self.purchase_order_1.account_payment_ids
        self.assertTrue(payment_1)
        self.assertEqual(payment_1.state, "in_process")

        # Change setting and create a second payment:
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_advance_payment.auto_post_advance_payments", False
        )
        advance_payment_2 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()
        payment_2 = self.purchase_order_1.account_payment_ids - payment_1
        self.assertEqual(len(payment_2), 1)
        self.assertEqual(payment_2.state, "draft")

    def test_07_auto_reconcile_advance_payment_enabled(self):
        # Set the config parameter to True
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
        # Set the config parameter to True
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_advance_payment.auto_reconcile_advance_payments", True
        )
        self.assertTrue(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment - USD - cash
        advance_payment_usd = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_usd.make_advance_payment()
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
        self.assertEqual(invoice.amount_residual, 3600)
        invoice.action_post()
        self.assertEqual(invoice.amount_residual, 3400)
        self.assertNotEqual(
            invoice.amount_residual,
            invoice.amount_total,
        )
        self.assertTrue(
            invoice.payment_state in ["partial"],
            "Advance payment should be reconciled automatically.",
        )

    def test_08_auto_reconcile_advance_payment_disabled(self):
        self.assertFalse(
            bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("purchase_advance_payment.auto_reconcile_advance_payments")
            )
        )

        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )
        context_payment = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        # Create Advance Payment - USD - cash
        advance_payment_usd = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.purchase_order_1.id,
                }
            )
        )
        advance_payment_usd.make_advance_payment()
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
        self.assertEqual(invoice.amount_residual, 3600)
        invoice.action_post()
        self.assertEqual(invoice.amount_residual, 3600)
        self.assertEqual(
            invoice.amount_residual,
            invoice.amount_total,
        )
        self.assertEqual(
            invoice.payment_state,
            "not_paid",
            "Advance payment should not be automatically reconciled "
            "when setting is disabled.",
        )

    def test_09_no_reconcile_when_no_matching_payment(self):
        # Set the config parameter to True
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_advance_payment.auto_reconcile_advance_payments", True
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )

        # Confirm Purchase Order
        self.purchase_order_1.button_confirm()
        self.assertEqual(self.purchase_order_1.invoice_status, "to invoice")

        # Create and post the invoice without making an advance payment
        self.purchase_order_1.action_create_invoice()
        self.assertEqual(self.purchase_order_1.invoice_status, "invoiced")
        self.assertEqual(self.purchase_order_1.amount_residual, 3600)
        invoice = self.purchase_order_1.invoice_ids
        invoice.write({"invoice_date": fields.Date.today()})
        invoice.action_post()
        self.assertEqual(invoice.amount_residual, 3600)
        self.assertEqual(
            invoice.amount_residual,
            invoice.amount_total,
        )
        # Ensure no reconciliation happens
        self.assertEqual(
            invoice.payment_state,
            "not_paid",
            "No reconciliation should happen without advance payments.",
        )

    def test_10_advance_payment_status_with_bill(self):
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            3600,
        )
        self.assertEqual(
            self.purchase_order_1.amount_residual,
            self.purchase_order_1.amount_total,
        )
        self.assertEqual(self.purchase_order_1.advance_payment_status, "not_paid")

        # Create Bill
        self.purchase_order_1.button_confirm()
        self.assertEqual(self.purchase_order_1.invoice_status, "to invoice")
        self.purchase_order_1.action_create_invoice()
        self.assertEqual(self.purchase_order_1.invoice_status, "invoiced")
        self.assertEqual(self.purchase_order_1.amount_residual, 3600)
        invoice = self.purchase_order_1.invoice_ids
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        self.assertEqual(self.purchase_order_1.advance_payment_status, "not_paid")

        # Create Payment 1
        active_ids = invoice.ids
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=active_ids
        ).create(
            {
                "amount": 200.0,
                "group_payment": True,
                "payment_difference_handling": "open",
            }
        )._create_payments()
        self.assertEqual(self.purchase_order_1.amount_residual, 3400)
        self.assertEqual(self.purchase_order_1.advance_payment_status, "partial")

        # Create Payment 2
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=active_ids
        ).create(
            {
                "amount": 3400.0,
                "group_payment": True,
                "payment_difference_handling": "open",
            }
        )._create_payments()
        self.assertEqual(self.purchase_order_1.amount_residual, 0)
        self.assertEqual(self.purchase_order_1.advance_payment_status, "paid")

    def test_11_advance_payments_without_account_moves(self):
        """Test full flow with advance payments without outstanding
        account."""
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_advance_payment.auto_post_advance_payments", False
        )
        self.purchase_order_2.button_confirm()
        self.assertEqual(
            self.purchase_order_2.amount_residual,
            1200,
        )

        context_payment = {
            "active_ids": [self.purchase_order_2.id],
            "active_id": self.purchase_order_2.id,
        }
        advance_payment_1 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "amount_advance": 300,
                    "order_id": self.purchase_order_2.id,
                }
            )
        )
        advance_payment_1.make_advance_payment()

        payment_1 = self.purchase_order_2.account_payment_ids
        self.assertFalse(payment_1.move_id)
        self.assertEqual(payment_1.state, "draft")
        if payment_1.outstanding_account_id:
            # This is forced by Odoo in EE. See
            # https://github.com/odoo/odoo/commit/0c2810df991b5ac48483f03d4cd0f5d281ece4b8
            # for more details. We remove it to simulate,
            # the case of a payment without journal entry.
            payment_1.outstanding_account_id = False
        payment_1.action_post()
        self.assertFalse(payment_1.move_id)
        self.assertEqual(payment_1.state, "in_process")

        self.assertEqual(self.purchase_order_2.amount_residual, 900)

        advance_payment_2 = (
            self.env["account.voucher.wizard.purchase"]
            .with_context(**context_payment)
            .create(
                {
                    "amount_advance": 200,
                    "order_id": self.purchase_order_2.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()

        # In the second payment, we confirm without removing the
        # outstanding account. In CE, this will create the
        # journal entry anyway, thefore we test the combination of
        # payments with and without entry.
        self.assertEqual(self.purchase_order_2.amount_residual, 900)
        payment_2 = self.purchase_order_2.account_payment_ids - payment_1
        self.assertEqual(len(payment_2), 1)
        payment_2.action_post()
        self.assertEqual(payment_2.state, "in_process")
        self.assertTrue(payment_2.move_id)

        self.assertEqual(self.purchase_order_2.amount_residual, 700)

        self.purchase_order_2.action_create_invoice()
        self.assertEqual(self.purchase_order_2.invoice_status, "invoiced")
        aml = self.env["account.move.line"].search(
            [("purchase_line_id", "=", self.purchase_order_2.order_line.id)]
        )
        invoice = aml.mapped("move_id")
        self.assertEqual(len(invoice), 1)
        self.assertFalse(invoice.matched_payment_ids)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        # We expect payment_1 linked to the invoice because
        # it has no move_id.
        self.assertEqual(invoice.matched_payment_ids, payment_1)
        self.assertEqual(invoice.amount_residual, 1200)
        self.assertEqual(
            self.purchase_order_2.amount_residual,
            1000,
            "Only payment 2 should be considered at this point.",
        )
