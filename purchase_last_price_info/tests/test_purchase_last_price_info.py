# Copyright 2019 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import odoo.tests.common as common
from odoo import fields


class TestPurchaseLastPriceInfo(common.TransactionCase):
    def setUp(self):
        super().setUp()
        usd = self.env.ref("base.USD")
        eur = self.env.ref("base.EUR")
        self.currency = self.env.ref("base.main_company").currency_id
        self.currency_extra = eur if self.currency == usd else usd
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.product = self.env.ref("product.consu_delivery_01")
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "standard_price": 10.0,
                "list_price": 20.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.partner = self.env.ref("base.res_partner_1")
        # Create custom rates to currency + currency_extra
        self._create_currency_rate(self.currency, "2000-01-01", 1.0)
        self._create_currency_rate(self.currency_extra, "2000-01-01", 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def test_purchase_last_price_info_demo(self):
        purchase_order = self.env.ref("purchase.purchase_order_6")
        purchase_order.write(
            {"date_order": "2000-01-01", "currency_id": self.currency.id}
        )
        purchase_order.button_confirm()
        purchase_lines = self.purchase_line_model.search(
            [
                ("product_id", "=", self.product.id),
                ("state", "in", ["purchase", "done"]),
            ]
        ).sorted(key=lambda line: line.order_id.date_order, reverse=True)
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
        self.assertEqual(self.product.last_purchase_currency_id, self.currency)
        self.assertEqual(self.product.last_purchase_price_currency, 1.0)

    def test_purchase_last_price_info_new_order(self):
        purchase_order1 = self.purchase_model.create(
            {
                "date_order": "2000-01-01",
                "currency_id": self.currency_extra.id,
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": self.product1.standard_price,
                            "name": self.product1.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "sequence": 1,
                        },
                    )
                ],
            }
        )
        purchase_order2 = self.purchase_model.create(
            {
                "date_order": "2001-01-01",
                "currency_id": self.currency_extra.id,
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": self.product1.standard_price,
                            "name": self.product1.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "sequence": 9999,
                        },
                    )
                ],
            }
        )
        purchase_order1.button_confirm()
        purchase_order2.button_confirm()
        self.assertEqual(
            purchase_order2.date_order,
            self.product1.last_purchase_date,
        )
        first_order_line = fields.first(
            self.product1.last_purchase_line_ids.sudo().filtered_domain(
                [
                    ("state", "in", ["purchase", "done"]),
                    ("company_id", "in", self.env.companies.ids),
                ]
            )
        )
        self.assertNotEqual(
            first_order_line.date_order,
            self.product1.last_purchase_date,
        )
        expected_date = datetime.datetime(2001, 1, 1, 0, 0)
        self.assertEqual(
            expected_date,
            self.product1.last_purchase_date,
        )
        expected_price = 10.0
        self.assertEqual(expected_price, self.product1.last_purchase_price)
        expected_currency = self.currency_extra
        self.assertEqual(
            expected_currency,
            self.product1.last_purchase_currency_id,
        )
        self.assertEqual(self.product1.last_purchase_currency_id, self.currency_extra)
        self.assertEqual(self.product1.last_purchase_price_currency, 2.0)
        self.assertEqual(self.partner, self.product1.last_purchase_supplier_id)
        purchase_order2.button_cancel()
        self.assertEqual(purchase_order2.state, "cancel")
