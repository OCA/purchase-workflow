# Copyright 2019 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import odoo.tests.common as common
from odoo import Command, fields


class TestPurchaseLastPriceInfo(common.TransactionCase):
    def setUp(self):
        super().setUp()
        usd = self.env.ref("base.USD")
        eur = self.env.ref("base.EUR")
        self.currency = self.env.ref("base.main_company").currency_id
        self.currency_extra = eur if self.currency == usd else usd
        self.product_model = self.env["product.product"]
        self.product_category_model = self.env["product.category"]
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]

        self.partner = self.env["res.partner"].create({"name": "Wood Corner Test"})
        self.product_category_furniture = self.product_category_model.create(
            {"name": "Furniture"}
        )
        self.product_category_office = self.product_category_model.create(
            {
                "name": "Office",
                "parent_id": self.product_category_furniture.id,
            }
        )
        self.product = self.product_model.create(
            {
                "name": "Two-Seat Sofa",
                "type": "consu",
                "standard_price": 1000.0,
                "list_price": 1500.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "description_sale": "Two-Seater Sofa with Oak Wood Frame",
                "default_code": "FURN_8999",
                "weight": 0.01,
                "categ_id": self.product_category_office.id,
            }
        )
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "standard_price": 10.0,
                "list_price": 20.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.product_2 = self.product_model.create(
            {
                "name": "Test product 2",
                "type": "consu",
                "standard_price": 1000.0,
                "list_price": 1500.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.product_3 = self.product_model.create(
            {
                "name": "Test product 3",
                "type": "consu",
                "standard_price": 1000.0,
                "list_price": 1500.0,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        # Create custom rates to currency + currency_extra
        self._create_currency_rate(self.currency, "2000-01-01", 1.0)
        self._create_currency_rate(self.currency_extra, "2000-01-01", 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def test_purchase_last_price_info_demo(self):
        purchase_order = self.purchase_model.create(
            {
                "partner_id": self.partner.id,
                "date_order": "2000-01-01",
                "currency_id": self.currency.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "name": self.product_2.name,
                            "price_unit": 58,
                            "product_qty": 9,
                            "product_uom_id": self.product_2.uom_id.id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.product_3.id,
                            "name": self.product_3.name,
                            "price_unit": 65,
                            "product_qty": 3,
                            "product_uom_id": self.product_3.uom_id.id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "price_unit": 154.5,
                            "product_qty": 4,
                            "product_uom_id": self.product.uom_id.id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                ],
            }
        )
        purchase_order.button_confirm()
        purchase_lines = self.purchase_line_model.search(
            [
                ("product_id", "=", self.product.id),
                ("state", "in", ["purchase", "done"]),
            ]
        ).sorted(key=lambda line: line.order_id.date_order, reverse=True)
        first_purchase_line = purchase_lines[:1]
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
        self.assertEqual(self.product.last_purchase_price_currency_rate, 1.0)

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
                            "product_uom_id": self.product1.uom_id.id,
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
                            "product_uom_id": self.product1.uom_id.id,
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
        first_order_line = (
            self.product1.last_purchase_line_ids.sudo().filtered_domain(
                [
                    ("state", "in", ["purchase", "done"]),
                    ("company_id", "in", self.env.companies.ids),
                ]
            )
        )[:1]
        last_purchase_line = self.product1.last_purchase_line_id
        last_purchase_line_tmp = self.product1.product_tmpl_id.last_purchase_line_id
        self.assertNotEqual(first_order_line, last_purchase_line)
        self.assertEqual(last_purchase_line, last_purchase_line_tmp)
        self.assertNotEqual(
            first_order_line.date_order,
            self.product1.last_purchase_date,
        )
        expected_date = datetime.datetime(2001, 1, 1, 0, 0)
        self.assertEqual(
            expected_date,
            self.product1.last_purchase_date,
        )
        self.assertEqual(
            last_purchase_line.date_order,
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
        self.assertEqual(self.product1.last_purchase_price_currency_rate, 2.0)
        self.assertEqual(self.partner, self.product1.last_purchase_supplier_id)
        purchase_order2.button_cancel()
        self.assertEqual(purchase_order2.state, "cancel")
