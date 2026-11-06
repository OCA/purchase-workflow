# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import tagged

from odoo.addons.purchase_request.tests.test_purchase_request import TestPurchaseRequest


@tagged("post_install", "-at_install")
class TestPurchaseRequestManualCurrency(TestPurchaseRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")
        cls.eur.write({"active": True})

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

    def test_01_purchase_request_manual_currency_company_rate(self):
        self.assertEqual(self.env.user.company_id.currency_id, self.usd)
        pr = self.purchase_request
        # Create a purchase request line
        vals = {
            "name": "Test line 1",
            "request_id": pr.id,
            "product_id": self.env.ref("product.product_product_6").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
            "estimated_cost": 100.0,
        }
        purchase_request_line = self.purchase_request_line_obj.create(vals)

        self.assertEqual(purchase_request_line.currency_id, self.usd)
        self.assertEqual(pr.currency_id, self.usd)
        self.assertEqual(pr.currency_rate, 1)
        self.assertEqual(pr.estimated_cost, pr.estimated_cost_cc)

        # Change currency to EUR and manual_currency
        with Form(pr) as p:
            p.currency_id = self.eur
            p.manual_currency = True
            p.type_currency = "company_rate"
        p.save()

        self.assertEqual(purchase_request_line.currency_id, self.eur)
        self.assertEqual(pr.currency_id, self.eur)
        self.assertEqual(pr.currency_rate, 5)
        self.assertEqual(pr.type_currency, "company_rate")
        # Rate for test is 5 EUR = 1 USD
        # So, estimated_cost_cc = 100 / 5 = 20 USD
        # estimated_cost = 100 EUR
        self.assertEqual(pr.estimated_cost_cc, pr.estimated_cost / 5)

        # Manual change currency rate to 2 EUR = 1 USD
        with Form(pr) as p:
            p.currency_rate = 2
        p.save()

        self.assertEqual(pr.currency_rate, 2)
        self.assertEqual(pr.type_currency, "company_rate")
        # Rate for test is 2 EUR = 1 USD
        # So, estimated_cost_cc = 100 / 2 = 50 USD
        # estimated_cost = 100 EUR
        self.assertEqual(pr.estimated_cost_cc, pr.estimated_cost / 2)

        pr.button_to_approve()
        self.assertEqual(pr.state, "to_approve")

        with self.assertRaisesRegex(
            UserError, "Rate currency can refresh state draft only."
        ):
            pr.action_refresh_currency()
        pr.button_draft()
        self.assertEqual(pr.state, "draft")
        pr.action_refresh_currency()
        self.assertEqual(pr.currency_rate, 5)

    def test_02_purchase_request_manual_currency_inverse_company_rate(self):
        self.assertEqual(self.env.user.company_id.currency_id, self.usd)
        pr = self.purchase_request
        # Create a purchase request line
        vals = {
            "name": "Test line 1",
            "request_id": pr.id,
            "product_id": self.env.ref("product.product_product_6").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
            "estimated_cost": 100.0,
        }
        purchase_request_line = self.purchase_request_line_obj.create(vals)

        self.assertEqual(purchase_request_line.currency_id, self.usd)
        self.assertEqual(pr.currency_id, self.usd)
        self.assertEqual(pr.currency_rate, 1)
        self.assertEqual(pr.estimated_cost, pr.estimated_cost_cc)

        # Change currency to EUR and manual_currency
        with Form(pr) as p:
            p.currency_id = self.eur
            p.manual_currency = True
            p.type_currency = "inverse_company_rate"
        p.save()

        self.assertEqual(purchase_request_line.currency_id, self.eur)
        self.assertEqual(pr.currency_id, self.eur)
        # Inverse, Currency Rate is 1 EUR = 0.2 USD
        self.assertEqual(pr.currency_rate, 0.2)
        self.assertEqual(pr.type_currency, "inverse_company_rate")
        # Rate for test is 1 EUR = 0.2 USD
        # So, estimated_cost_cc = 100 * 0.2 = 20 USD
        # estimated_cost = 100 EUR
        self.assertEqual(pr.estimated_cost_cc, pr.estimated_cost * pr.currency_rate)

        # Manual change currency rate to 2 EUR = 1 USD
        with Form(pr) as p:
            p.currency_rate = 2
        p.save()

        self.assertEqual(pr.currency_rate, 2)
        self.assertEqual(pr.type_currency, "inverse_company_rate")
        # Rate for test is 1 EUR = 2 USD
        # So, estimated_cost_cc = 100 * 2 = 200 USD
        # estimated_cost = 100 EUR
        self.assertEqual(pr.estimated_cost_cc, pr.estimated_cost * 2)

        pr.action_refresh_currency()
        self.assertEqual(pr.currency_rate, 0.2)
