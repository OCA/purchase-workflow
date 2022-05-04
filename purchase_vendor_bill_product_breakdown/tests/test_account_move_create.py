from odoo import fields
from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestAccountMoveCreate(common.TransactionCase):
    def setUp(self):
        super(TestAccountMoveCreate, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductProduct = self.env["product.product"]
        self.AccountMove = self.env["account.move"]
        self.bank_journal_euro = self.env["account.journal"].create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BNK67",
                "company_id": self.env.user.company_id.id,
            }
        )
        self.account_euro = self.bank_journal_euro.default_account_id
        self.res_partner_test = ResPartner.create(
            {
                "name": "Test Partner",
            }
        )
        self.currency_id = self.env.ref("base.EUR").id

        uom_unit_id = self.ref("uom.product_uom_unit")

        self.product_product_test_1 = ProductProduct.create(
            {
                "name": "Test Product #1",
                "standard_price": 100.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_test_2 = ProductProduct.create(
            {
                "name": "Test Product #2",
                "standard_price": 100.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

    def test_account_move_skip_one_line(self):
        account_move_test_1 = self.AccountMove.create(
            {
                "move_type": "in_refund",
                "partner_id": self.res_partner_test.id,
                "invoice_date": fields.Date.from_string("2022-01-01"),
                "currency_id": self.currency_id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.product_product_test_1.id,
                            "quantity": 3,
                            "price_unit": 300,
                            "skip_record": True,
                            "account_id": self.account_euro.id,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "product_id": self.product_product_test_2.id,
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": self.account_euro.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            len(account_move_test_1.invoice_line_ids),
            1,
            msg="Count invoice lines must be equal 1",
        )

    def test_account_move_default_handle(self):
        account_move_test_2 = self.AccountMove.create(
            {
                "move_type": "in_refund",
                "partner_id": self.res_partner_test.id,
                "invoice_date": fields.Date.from_string("2022-01-01"),
                "currency_id": self.currency_id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "quantity": 3,
                            "price_unit": 300,
                            "account_id": self.account_euro.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_2.id,
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": self.account_euro.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            len(account_move_test_2.invoice_line_ids),
            2,
            msg="Count invoice lines must be equal 2",
        )

    def test_account_move_skip_all_line(self):
        account_move_test_3 = self.AccountMove.create(
            {
                "move_type": "in_refund",
                "partner_id": self.res_partner_test.id,
                "invoice_date": fields.Date.from_string("2022-01-01"),
                "currency_id": self.currency_id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.product_product_test_1.id,
                            "quantity": 3,
                            "price_unit": 300,
                            "skip_record": True,
                            "account_id": self.account_euro.id,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "product_id": self.product_product_test_2.id,
                            "quantity": 1,
                            "price_unit": 100,
                            "skip_record": True,
                            "account_id": self.account_euro.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            len(account_move_test_3.invoice_line_ids),
            0,
            msg="Count invoice lines must be equal 0",
        )

    def test_account_move_empty_key(self):
        account_move_test_4 = self.AccountMove.create(
            {
                "move_type": "in_refund",
                "partner_id": self.res_partner_test.id,
                "invoice_date": fields.Date.from_string("2022-01-01"),
                "currency_id": self.currency_id,
            }
        )
        self.assertEqual(
            len(account_move_test_4.invoice_line_ids),
            0,
            msg="Count invoice lines must be equal 0",
        )
