# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseManualCurrency(TransactionCase):
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
        self.purchase_order = self.env.ref("purchase.purchase_order_6").copy()

    def test_01_purchase_manual_currency(self):
        # Update purchase to company currency
        self.purchase_order.currency_id = self.currency_eur
        self.assertEqual(self.purchase_order.currency_id.name, "EUR")
        self.assertEqual(
            self.purchase_order.order_line[0].price_subtotal,
            self.purchase_order.order_line[0].subtotal_company_currency,
        )
        self.assertFalse(self.purchase_order.currency_diff)

        # Activate Multi Currency Group
        multi_currency_group = self.env.ref("base.group_multi_currency")
        self.env.user.groups_id |= multi_currency_group

        # Change currency
        self.assertEqual(self.purchase_order.manual_currency_rate, 0.0)
        with Form(self.purchase_order) as p:
            p.currency_id = self.currency_usd
            p.manual_currency = True
            p.type_currency = "company_rate"
        # Manual currency rate will default following rate standard
        self.assertNotEqual(self.purchase_order.manual_currency_rate, 0.0)
        self.assertNotEqual(
            self.purchase_order.order_line[0].price_subtotal,
            self.purchase_order.order_line[0].subtotal_company_currency,
        )
        company_rate = self.purchase_order.manual_currency_rate
        # Check type curreny -> company currency (USD -> EUR)
        with Form(self.purchase_order) as p:
            p.type_currency = "inverse_company_rate"
        self.assertEqual(
            round(self.purchase_order.manual_currency_rate, 8),
            round(1 / company_rate, 8),
        )
        # Check function refresh
        currency_rate = self.purchase_order.manual_currency_rate
        self.purchase_order.manual_currency_rate += 5.0
        self.assertNotEqual(self.purchase_order.manual_currency_rate, currency_rate)
        self.purchase_order.action_refresh_currency()
        self.assertAlmostEqual(self.purchase_order.manual_currency_rate, currency_rate)
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.state, "purchase")
        with self.assertRaises(ValidationError):
            self.purchase_order.action_refresh_currency()
