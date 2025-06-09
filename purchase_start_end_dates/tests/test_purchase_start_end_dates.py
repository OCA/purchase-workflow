# Copyright 2022 elego Software Solutions, Germany (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseStartEndDates(TransactionCase):
    def setUp(self):
        super().setUp()
        self.AccountInvoice = self.env["account.move"]
        self.partner = self.env.ref("base.res_partner_1")
        uom_unit = self.env.ref("uom.product_uom_unit")
        self.product_id = self.env["product.product"].create(
            {
                "name": "Product",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PRODUCT",
                "taxes_id": False,
                "must_have_dates": True,
            }
        )
        self.default_start_date = datetime.datetime.now()
        self.default_end_date = self.default_start_date + datetime.timedelta(days=9)
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "default_start_date": self.default_start_date,
                "default_end_date": self.default_end_date,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id.name,
                            "product_id": self.product_id.id,
                            "product_qty": 2,
                            "product_uom": self.product_id.uom_id.id,
                            "price_unit": self.product_id.list_price,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        self.po.button_confirm()
        for po_lines in self.po.order_line:
            po_lines.write(
                {
                    "start_date": self.default_start_date,
                    "end_date": self.default_end_date,
                }
            )

    def test_default_start_date_change(self):
        with self.assertRaises(ValidationError):
            self.po.write(
                {
                    "default_start_date": self.default_end_date,
                    "default_end_date": self.default_start_date,
                }
            )
        self.po.default_start_date_change()

    def test_default_end_date_change(self):
        with self.assertRaises(ValidationError):
            self.po.write(
                {
                    "default_start_date": self.default_end_date,
                    "default_end_date": self.default_start_date,
                }
            )
        self.po.default_end_date_change()

    def test_start_end_dates_product_id_change(self):
        if self.po.default_end_date and self.po.default_end_date:
            self.po.order_line.start_end_dates_product_id_change()
            self.po.order_line.start_date_change()
            self.po.order_line.end_date_change()

    def test_start_end_dates_product_id(self):
        self.product_id.must_have_dates = False
        self.po.default_start_date = self.po.default_end_date = False
        self.po.order_line.start_end_dates_product_id_change()

    def test_end_date_change(self):
        self.product_id.must_have_dates = False
        self.po.order_line.write(
            {"start_date": self.default_end_date, "end_date": self.default_start_date}
        )
        self.po.order_line.end_date_change()

    def test_start_date_change(self):
        self.product_id.must_have_dates = False
        self.po.order_line.write(
            {"start_date": self.default_end_date, "end_date": self.default_start_date}
        )
        self.po.order_line.start_date_change()

    def test_constrains_end_dates(self):
        with self.assertRaises(ValidationError):
            self.po.order_line.end_date = False

    def test_constrains_start_date(self):
        with self.assertRaises(ValidationError):
            self.po.order_line.start_date = False

    def test_constrains_greater_st_date(self):
        with self.assertRaises(ValidationError):
            self.po.order_line.write(
                {
                    "start_date": self.default_end_date,
                    "end_date": self.default_start_date,
                }
            )

    def test_compute_number_of_days(self):
        self.assertEqual(self.po.order_line[0].number_of_days, 10)

    def test_inverse_number_of_days(self):
        self.po.order_line[0].number_of_days = 1
        self.assertEqual(
            self.po.order_line[0].start_date, self.po.order_line[0].end_date
        )

    def test_vendor_bill_start_end_date(self):
        action = self.po.action_create_invoice()
        self.invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(
            self.invoice.invoice_line_ids.mapped("start_date")[0],
            self.default_start_date.date(),
        )
        self.assertEqual(
            self.invoice.invoice_line_ids.mapped("end_date")[0],
            self.default_end_date.date(),
        )
