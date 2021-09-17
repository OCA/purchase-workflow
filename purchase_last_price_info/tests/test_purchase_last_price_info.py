# Copyright 2019 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestPurchaseLastPriceInfo(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.currency_usd = self.env.ref("base.USD")
        self.currency_eur = self.env.ref("base.EUR")
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.product = self.env.ref("product.consu_delivery_01")
        self.partner = self.env.ref("base.res_partner_1")
        # Create custom rates to USD + EUR
        self._create_currency_rate(self.currency_usd, "2000-01-01", 1.0)
        self._create_currency_rate(self.currency_eur, "2000-01-01", 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def test_purchase_last_price_info_demo(self):
        purchase_order = self.env.ref("purchase.purchase_order_6")
        purchase_order.write(
            {"date_order": "2000-01-01", "currency_id": self.currency_usd.id}
        )
        purchase_order.button_confirm()
        purchase_lines = self.purchase_line_model.search(
            [
                ("product_id", "=", self.product.id),
                ("state", "in", ["purchase", "done"]),
            ]
        ).sorted(key=lambda l: l.order_id.date_order, reverse=True)
        first_purchase_line = fields.first(purchase_lines)
        self.assertEqual(
            fields.Datetime.from_string(first_purchase_line.order_id.date_order).date(),
            fields.Datetime.from_string(self.product.last_purchase_date).date(),
        )
        self.assertEqual(
            first_purchase_line.price_unit, self.product.last_purchase_price
        )
        self.assertEqual(
            first_purchase_line.order_id.partner_id,
            self.product.last_purchase_supplier_id,
        )
        self.assertEqual(
            first_purchase_line.currency_id, self.product.last_purchase_currency_id
        )
        self.assertEqual(self.product.last_purchase_currency_id, self.currency_usd)
        self.assertEqual(self.product.last_purchase_price_currency, 1.0)

    def test_purchase_last_price_info_new_order(self):
        purchase_order = self.purchase_model.create(
            {
                "date_order": "2000-01-01",
                "currency_id": self.currency_eur.id,
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.standard_price,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.assertEqual(
            fields.Datetime.from_string(purchase_order.date_order).date(),
            fields.Datetime.from_string(self.product.last_purchase_date).date(),
        )
        first_order_line = fields.first(purchase_order.order_line)
        self.assertEqual(first_order_line.price_unit, self.product.last_purchase_price)
        self.assertEqual(first_order_line.price_unit, self.product.last_purchase_price)
        self.assertEqual(self.product.last_purchase_currency_id, self.currency_eur)
        self.assertEqual(self.product.last_purchase_price_currency, 2.0)
        self.assertEqual(self.partner, self.product.last_purchase_supplier_id)
        purchase_order.button_cancel()
        self.assertEqual(purchase_order.state, "cancel")
