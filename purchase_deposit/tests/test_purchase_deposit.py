# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseDeposit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.account_model = cls.env["account.account"]
        cls.invoice_model = cls.env["account.move"]

        # Create Deposit Account
        cls.account_deposit = cls.account_model.create(
            {
                "name": "Purchase Deposit",
                "code": "11620",
                "account_type": "asset_current",
            }
        )
        # Create products:
        p1 = cls.product1 = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "service",
                "default_code": "PROD1",
                "purchase_method": "purchase",
            }
        )

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": p1.id,
                            "product_uom": p1.uom_id.id,
                            "name": p1.name,
                            "price_unit": 100.0,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 42.0,
                        },
                    )
                ],
            }
        )

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 20",
                "type_tax_use": "purchase",
                "amount": 20,
            }
        )

    def create_advance_payment_form(self):
        ctx = {
            "active_id": self.po.id,
            "active_ids": [self.po.id],
            "active_model": "purchase.order",
            "create_bills": True,
        }
        CreateDeposit = self.env["purchase.advance.payment.inv"]
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")
        advance_form = Form(CreateDeposit.with_context(**ctx))
        return advance_form

    def test_create_deposit_invoice(self):
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        f = self.create_advance_payment_form()
        f.advance_payment_method = "percentage"
        wizard = f.save()
        wizard.amount = 10.0  # 10%
        wizard.deposit_account_id = self.account_deposit
        wizard.create_invoices()
        # New Purchase Deposit is created automatically
        deposit = self.env.company.purchase_deposit_product_id
        self.assertEqual(deposit.name, "Purchase Deposit")
        # 1 Deposit Invoice is created
        self.assertRecordValues(
            self.po.invoice_ids.invoice_line_ids,
            [
                {
                    "product_id": deposit.id,
                    "price_unit": 420.0,
                    "name": "Deposit Payment",
                }
            ],
        )
        # On Purchase Order, there will be new deposit line create
        self.assertRecordValues(
            self.po.order_line.filtered(lambda li: not li.display_type),
            [
                {
                    "product_id": self.product1.id,
                    "price_unit": 100.0,
                    "is_deposit": False,
                },
                {"product_id": deposit.id, "price_unit": 420.0, "is_deposit": True},
            ],
        )
        # On Purchase Order, create normal billing
        res = self.po.with_context(create_bill=True).action_create_invoice()
        invoice = self.invoice_model.browse(res["res_id"])
        self.assertRecordValues(
            invoice.invoice_line_ids.filtered(lambda li: li.display_type == "product"),
            [
                {"product_id": self.product1.id, "price_unit": 100.0, "quantity": 42},
                {"product_id": deposit.id, "price_unit": 420.0, "quantity": -1},
            ],
        )

    def test_create_deposit_invoice_exception_1(self):
        """This test focus on exception cases, when create deposit invoice,
        1. This action is allowed only in Purchase Order sate
        2. The value of the deposit must be positive
        3. For type percentage, The percentage of the deposit must <= 100
        """
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        # 1. The value of the deposit must be positive
        f = self.create_advance_payment_form()
        f.advance_payment_method = "fixed"
        f.amount = 0.0
        f.deposit_account_id = self.account_deposit
        wizard = f.save()
        with self.assertRaises(UserError):
            wizard.create_invoices()
        # 2. For type percentage, The percentage of the deposit must <= 100
        wizard.advance_payment_method = "percentage"
        wizard.amount = 101.0
        with self.assertRaises(UserError):
            wizard.create_invoices()
        wizard.amount = 10

    def test_create_deposit_invoice_exception_2(self):
        """This test focus on exception cases, when create deposit invoice,
        4. Purchase Deposit Product's purchase_method != purchase
        """
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        f = self.create_advance_payment_form()
        f.advance_payment_method = "percentage"
        f.amount = 101.0
        f.deposit_account_id = self.account_deposit
        wizard = f.save()
        # 4. Purchase Deposit Product's purchase_method != purchase
        deposit = self.env.company.purchase_deposit_product_id
        deposit.purchase_method = "receive"
        wizard.purchase_deposit_product_id = deposit
        with self.assertRaises(UserError):
            wizard.create_invoices()

    def test_create_deposit_invoice_exception_3(self):
        """This test focus on exception cases, when create deposit invoice,
        5. Purchase Deposit Product's type != service
        """
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        f = self.create_advance_payment_form()
        f.advance_payment_method = "percentage"
        f.amount = 101.0
        f.deposit_account_id = self.account_deposit
        wizard = f.save()
        deposit = self.env.company.purchase_deposit_product_id
        # 5. Purchase Deposit Product's type != service
        deposit.type = "consu"
        with self.assertRaises(UserError):
            wizard.create_invoices()

    def test_deposit_invoice_update_price_and_taxes(self):
        f = self.create_advance_payment_form()
        f.advance_payment_method = "percentage"
        wizard = f.save()
        wizard.amount = 10.0
        wizard.deposit_account_id = self.account_deposit
        wizard.create_invoices()
        # New Purchase Deposit is created automatically
        deposit = self.env.company.purchase_deposit_product_id
        self.assertEqual(deposit.name, "Purchase Deposit")
        self.po.invoice_ids.invoice_date = fields.Date.today()
        self.po.invoice_ids.invoice_line_ids.write(
            {
                "price_unit": 500.0,
                "tax_ids": [(6, 0, [self.tax.id])],
            }
        )
        self.po.invoice_ids.action_post()
        deposit_line = self.po.order_line.filtered(
            lambda p: p.is_deposit and not p.display_type
        )
        self.assertEqual(deposit_line.price_unit, 500.0)
        self.assertEqual(deposit_line.taxes_id.id, self.tax.id)
