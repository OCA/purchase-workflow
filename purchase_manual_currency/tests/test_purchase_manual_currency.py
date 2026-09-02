# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestPurchaseManualCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.main_currency = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")
        cls.eur.write({"active": True})

        cls.purchase_model = cls.env["purchase.order"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")

        # Fixed currency rate
        cls.eur.rate_ids.unlink()
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.eur.id,
                "rate": 5,
                "create_date": "2010-01-01",
                "write_date": "2010-01-01",
            }
        )

    def test_01_purchase_main_currency(self):
        """Case1: Use main currency"""

        po = self.purchase_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )

        self.assertEqual(po.currency_id.name, "USD")
        self.assertEqual(
            po.order_line.price_subtotal,
            po.order_line.subtotal_company_currency,
        )
        self.assertEqual(po.currency_rate, 1)

    def test_02_purchase_manual_currency_company_rate(self):
        """Case2: Use manual currency with company rate"""

        po = self.purchase_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )

        self.assertEqual(po.currency_id.name, "USD")
        with Form(po) as p:
            p.currency_id = self.eur
            p.manual_currency = True
            p.type_currency = "company_rate"
        p.save()
        self.assertEqual(po.currency_id.name, "EUR")
        # Standard Currency
        self.assertEqual(po.currency_rate, 5)
        self.assertEqual(po.type_currency, "company_rate")

        self.assertEqual(po.order_line.price_subtotal, 100)
        self.assertEqual(po.order_line.subtotal_company_currency, 100 / 5)

        # Rate for test is 5 EUR = 1 USD
        # So, amount_total_cc = 100 / 5 = 20 USD
        # amount_total = 100 EUR
        self.assertEqual(po.amount_total_cc, 20.0)
        self.assertEqual(po.amount_total, 100.0)

        # Manual change currency rate to 2 EUR = 1 USD
        with Form(po) as p:
            p.currency_rate = 2
        p.save()

        self.assertEqual(po.currency_rate, 2)
        self.assertEqual(po.type_currency, "company_rate")
        # Rate for test is 2 EUR = 1 USD
        # So, amount_total_cc = 100 / 2 = 50 USD
        # amount_total = 100 EUR
        self.assertEqual(
            po.order_line.subtotal_company_currency, po.order_line.price_subtotal / 2
        )
        self.assertEqual(po.amount_total_cc, 50.0)
        self.assertEqual(po.amount_total, 100.0)

        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        with self.assertRaisesRegex(
            ValidationError, "Rate currency can refresh state draft only."
        ):
            po.action_refresh_currency()
        po.button_draft()
        self.assertEqual(po.state, "draft")
        po.action_refresh_currency()
        self.assertEqual(po.currency_rate, 5)

    def test_03_purchase_manual_currency_inverse_company_rate(self):
        """Case2: Use manual currency with inverse_company rate"""

        po = self.purchase_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )

        self.assertEqual(po.currency_id.name, "USD")
        with Form(po) as p:
            p.currency_id = self.eur
            p.manual_currency = True
            p.type_currency = "inverse_company_rate"
        p.save()
        self.assertEqual(po.currency_id.name, "EUR")

        # Inverse, Currency Rate is 1 EUR = 0.2 USD
        self.assertEqual(po.currency_rate, 0.2)
        self.assertEqual(po.type_currency, "inverse_company_rate")
        # Rate for test is 1 EUR = 0.2 USD
        # So, amount_total_cc = 100 * 0.2 = 20 USD
        # amount_total = 100 EUR
        self.assertEqual(po.order_line.price_subtotal, 100)
        self.assertEqual(po.order_line.subtotal_company_currency, 100 * 0.2)
        self.assertEqual(po.amount_total_cc, 20.0)
        self.assertEqual(po.amount_total, 100.0)

        # Manual change currency rate to 2 EUR = 1 USD
        with Form(po) as p:
            p.currency_rate = 2
        p.save()

        self.assertEqual(po.currency_rate, 2)
        self.assertEqual(po.type_currency, "inverse_company_rate")
        # Rate for test is 2 EUR = 1 USD
        # So, amount_total_cc = 100 * 2 = 200 USD
        # amount_total = 100 EUR
        self.assertEqual(
            po.order_line.subtotal_company_currency, po.order_line.price_subtotal * 2
        )
        self.assertEqual(po.amount_total_cc, 200.0)
        self.assertEqual(po.amount_total, 100.0)

        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        with self.assertRaisesRegex(
            ValidationError, "Rate currency can refresh state draft only."
        ):
            po.action_refresh_currency()
        po.button_draft()
        self.assertEqual(po.state, "draft")
        po.action_refresh_currency()
        self.assertEqual(po.currency_rate, 0.2)
