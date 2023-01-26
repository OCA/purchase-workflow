# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseRequestManualCurrency(TransactionCase):
    def setUp(self):
        super().setUp()
        self.currency_eur = self.env.ref("base.EUR")
        self.currency_usd = self.env.ref("base.USD")
        self.main_company = self.env.ref("base.main_company")
        self.env.cr.execute(
            """UPDATE res_company SET currency_id = %s
            WHERE id = %s""",
            (self.currency_eur.id, self.main_company.id),
        )
        self.product1 = self.env.ref("product.product_product_7")

    def _create_purchase_request(self, pr_lines):
        PurchaseRequest = self.env["purchase.request"]
        view_id = "purchase_request.view_purchase_request_form"
        with Form(PurchaseRequest, view=view_id) as pr:
            for pr_line in pr_lines:
                with pr.line_ids.new() as line:
                    line.product_id = pr_line["product_id"]
                    line.product_qty = pr_line["product_qty"]
                    line.estimated_cost = pr_line["estimated_cost"]
        purchase_request = pr.save()
        return purchase_request

    def test_01_purchase_request_manual_currency(self):
        purchase_request = self._create_purchase_request(
            [
                {
                    "product_id": self.product1,
                    "product_qty": 1,
                    "estimated_cost": 100,
                },
            ]
        )
        self.assertEqual(purchase_request.currency_id.name, "EUR")
        self.assertEqual(
            purchase_request.line_ids[0].estimated_cost,
            purchase_request.line_ids[0].estimated_cost_company_currency,
        )
        self.assertFalse(purchase_request.currency_diff)
        # use manual currency
        self.assertEqual(purchase_request.manual_currency_rate, 1)
        with Form(purchase_request) as pr:
            pr.currency_id = self.currency_usd
            pr.manual_currency = True
            pr.type_currency = "company_rate"
        self.assertNotEqual(purchase_request.manual_currency_rate, 1)
        self.assertNotEqual(
            purchase_request.line_ids[0].estimated_cost,
            purchase_request.line_ids[0].estimated_cost_company_currency,
        )
        company_rate = purchase_request.manual_currency_rate
        # Check type curreny -> company currency (USD -> EUR)
        with Form(purchase_request) as pr:
            pr.type_currency = "inverse_company_rate"
        self.assertEqual(
            round(purchase_request.manual_currency_rate, 8), round(1 / company_rate, 8)
        )
        currency_rate = purchase_request.manual_currency_rate
        # Change manual rate to 100.0
        purchase_request.manual_currency_rate = 100.0
        self.assertNotEqual(purchase_request.manual_currency_rate, currency_rate)
        # Check refresh currency, it should back to normal
        purchase_request.action_refresh_currency()
        self.assertAlmostEqual(purchase_request.manual_currency_rate, currency_rate)
        purchase_request.button_to_approve()
        self.assertEqual(purchase_request.state, "to_approve")
        # Check refresh currency can't do it when state is not draft
        with self.assertRaises(UserError):
            purchase_request.action_refresh_currency()
