# Copyright 2026 ADHOC SA (https://www.adhoc.com.ar)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import TransactionCase


class TestPurchaseDepositMultiCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Order currency worth 1000 times the company one
        cls.order_currency = cls.env["res.currency"].create(
            {
                "name": "PDX",
                "symbol": "PDX",
                "rate_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "2020-01-01",
                            "rate": 0.001,
                            "company_id": cls.env.company.id,
                        },
                    )
                ],
            }
        )
        cls.account_expense = cls.env["account.account"].search(
            [("account_type", "=", "expense")], limit=1
        )
        cls.deposit_product = cls._create_service("Purchase Deposit")
        product = cls._create_service("Test Product")
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env["res.partner"].create({"name": "Vendor"}).id,
                "currency_id": cls.order_currency.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                            "name": product.name,
                            "price_unit": 100.0,
                            "product_qty": 10.0,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po.button_confirm()

    @classmethod
    def _create_service(cls, name):
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "service",
                "purchase_method": "purchase",
                "property_account_expense_id": cls.account_expense.id,
            }
        )

    def test_deposit_billed_in_another_currency(self):
        """Posting a bill must not leak its currency figure into the order."""
        self.env["purchase.advance.payment.inv"].with_context(
            active_id=self.po.id,
            active_ids=self.po.ids,
            active_model="purchase.order",
        ).create(
            {
                "advance_payment_method": "fixed",
                "amount": 300.0,
                "purchase_deposit_product_id": self.deposit_product.id,
            }
        ).create_invoices()
        deposit_line = self.po.order_line.filtered("is_deposit")
        self.assertEqual(deposit_line.price_unit, 300.0)

        # The vendor bills the deposit in the company currency instead
        bill = self.po.invoice_ids
        bill.invoice_date = fields.Date.today()
        bill.currency_id = self.env.company.currency_id
        bill.invoice_line_ids.price_unit = 300000.0
        bill.action_post()

        self.assertEqual(deposit_line.price_unit, 300.0)
