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
            (self.main_company.id, self.currency_eur.id),
        )
        self.purchase_order = self.env.ref("purchase.purchase_order_6")

    def test_01_purchase_manual_currency(self):
        # Update purchase to main currency
        self.purchase_order.currency_id = self.currency_eur
        self.assertEqual(self.purchase_order.currency_id.name, "EUR")
        # change currency
        self.assertEqual(self.purchase_order.custom_rate, 0.0)
        with Form(self.purchase_order) as p:
            p.currency_id = self.currency_usd
            p.manual_currency = True
        self.assertNotEqual(self.purchase_order.custom_rate, 0.0)
        # check function refresh
        currency_rate = self.purchase_order.custom_rate
        self.purchase_order.custom_rate += 5.0
        self.assertNotEqual(self.purchase_order.custom_rate, currency_rate)
        self.purchase_order.action_refresh_currency()
        self.assertAlmostEqual(self.purchase_order.custom_rate, currency_rate)
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.state, "purchase")
        with self.assertRaises(ValidationError):
            self.purchase_order.action_refresh_currency()
