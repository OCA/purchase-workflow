# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseTaxAdjust(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Partners
        cls.partner_1 = cls.env.ref("base.res_partner_2")

        # Products
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_1.purchase_method = "purchase"

        cls.company = cls.env.ref("base.main_company")
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 20",
                "type_tax_use": "purchase",
                "amount": 20,
            }
        )

    def _create_purchase(self, price_unit, count_line):
        Purchase = self.env["purchase.order"]
        view_id = "purchase.purchase_order_form"
        with Form(Purchase, view=view_id) as po:
            po.partner_id = self.partner_1
            for i in range(count_line):
                with po.order_line.new() as line:
                    line.sequence = i
                    line.product_id = self.product_1
                    line.product_qty = 1.0
                    line.price_unit = price_unit
        purchase = po.save()
        return purchase

    def test_01_purchase_tax_adjust(self):
        purchase = self._create_purchase(100.0, 2)
        # Add tax in line
        purchase.order_line[0].taxes_id = [(6, 0, self.tax.ids)]
        purchase.order_line[1].taxes_id = [(6, 0, self.tax.ids)]
        json_vals = json.loads(purchase.tax_totals_json)
        # Check amount total PO
        self.assertAlmostEqual(purchase.amount_untaxed, 200)
        self.assertAlmostEqual(purchase.amount_tax, 40)
        self.assertAlmostEqual(purchase.amount_total, 240)
        self.assertAlmostEqual(purchase.order_line[0].price_tax, 20)
        self.assertAlmostEqual(purchase.order_line[1].price_tax, 20)
        # Adjust tax from 40.0 to 15.0, diff = 25
        json_vals["groups_by_subtotal"]["Untaxed Amount"][0]["tax_group_amount"] = 15.0
        with Form(purchase) as p:
            p.tax_totals_json = json.dumps(json_vals)
        p.save()
        self.assertAlmostEqual(purchase.order_line[0].price_tax, 1)
        self.assertAlmostEqual(purchase.order_line[1].price_tax, 14)

        # Check change price_unit in line, it should auto update refresh tax
        with Form(purchase.order_line[1]) as line:
            line.price_unit = 200
        line.save()
        self.assertAlmostEqual(purchase.order_line[0].price_tax, 20)
        # Line tax adjust will auto update
        self.assertAlmostEqual(purchase.order_line[1].price_tax, 40)

        # Check adjust tax less than count line
        json_vals["groups_by_subtotal"]["Untaxed Amount"][0]["tax_group_amount"] = 1.0
        with self.assertRaises(UserError):
            with Form(purchase) as p:
                p.tax_totals_json = json.dumps(json_vals)
