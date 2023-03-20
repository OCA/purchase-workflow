# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
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
        self.purchase_order_model = self.env["purchase.order"]
        self.partner1 = self.env.ref("base.res_partner_1")

    def _create_purchase_aggrement(self, pr_lines):
        # view_id = "purchase_request.view_purchase_request_form"
        with Form(self.env["purchase.requisition"]) as pr:
            for pr_line in pr_lines:
                with pr.line_ids.new() as line:
                    line.product_id = pr_line["product_id"]
                    line.product_qty = pr_line["product_qty"]
                    line.price_unit = pr_line["price_unit"]
        purchase_requisition = pr.save()
        return purchase_requisition

    def test_01_purchase_requisition_manual_currency(self):
        purchase_requisition = self._create_purchase_aggrement(
            [
                {
                    "product_id": self.product1,
                    "product_qty": 2,
                    "price_unit": 100,
                },
            ]
        )
        self.assertEqual(purchase_requisition.currency_id.name, "EUR")
        pr_line = purchase_requisition.line_ids[0]
        self.assertEqual(
            pr_line.price_unit * pr_line.product_qty,
            pr_line.subtotal_company_currency,
        )
        self.assertFalse(purchase_requisition.currency_diff)
        # use manual currency
        self.assertEqual(purchase_requisition.custom_rate, 1)
        with Form(purchase_requisition) as pr:
            pr.currency_id = self.currency_usd
            pr.manual_currency = True
            pr.type_currency = "company_rate"
        self.assertNotEqual(purchase_requisition.custom_rate, 1)
        pr_line = purchase_requisition.line_ids[0]
        self.assertNotEqual(
            pr_line.price_unit * pr_line.product_qty,
            pr_line.subtotal_company_currency,
        )
        company_rate = purchase_requisition.custom_rate
        # Check type curreny -> company currency (USD -> EUR)
        with Form(purchase_requisition) as pr:
            pr.type_currency = "inverse_company_rate"
        self.assertEqual(
            round(purchase_requisition.custom_rate, 8), round(1 / company_rate, 8)
        )
        currency_rate = purchase_requisition.custom_rate
        # Change manual rate to 100.0
        purchase_requisition.custom_rate = 100.0
        self.assertNotEqual(purchase_requisition.custom_rate, currency_rate)
        # Check refresh currency, it should back to normal
        purchase_requisition.action_refresh_currency()
        self.assertAlmostEqual(purchase_requisition.custom_rate, currency_rate)
        purchase_requisition.action_in_progress()
        self.assertEqual(purchase_requisition.state, "in_progress")
        # Check refresh currency can't do it when state is not draft
        with self.assertRaises(UserError):
            purchase_requisition.action_refresh_currency()

    def test_02_purchase_requisition_to_purchase_manual_currency(self):
        purchase_requisition = self._create_purchase_aggrement(
            [
                {
                    "product_id": self.product1,
                    "product_qty": 2,
                    "price_unit": 100,
                },
            ]
        )
        with Form(purchase_requisition) as pr:
            pr.currency_id = self.currency_usd
            pr.manual_currency = True
            pr.type_currency = "inverse_company_rate"
            pr.custom_rate = 100.0
        purchase_requisition.action_in_progress()
        self.assertEqual(purchase_requisition.state, "in_progress")

        # Create PO and link to purchase requisition
        with Form(self.purchase_order_model) as po:
            po.partner_id = self.partner1
            po.requisition_id = purchase_requisition
        purchase = po.save()
        # Manual currency of PO should same as Purchase Requisition
        self.assertEqual(purchase.manual_currency, purchase_requisition.manual_currency)
        self.assertEqual(purchase.type_currency, purchase_requisition.type_currency)
        self.assertEqual(purchase.custom_rate, purchase_requisition.custom_rate)
