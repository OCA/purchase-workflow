# Copyright 2024 Akretion - Clément Mombereau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderQtyChangeNoZero(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_1 = self.env["product.product"].create(
            {"name": "Test Product 1", "standard_price": 0, "taxes_id": False}
        )
        self.product_2 = self.env["product.product"].create(
            {"name": "Test Product 2", "standard_price": 30.00, "taxes_id": False}
        )
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.env.ref("base.res_partner_12")

        with purchase_form.order_line.new() as self.line_form:
            self.line_form.product_id = self.product_1
            self.line_form.product_qty = 1

    def test_product_with_standard_price_zero(self):
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 10)

        self.line_form.product_qty = 2
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)

    def test_product_with_standard_price_not_zero(self):
        self.line_form.product_id = self.product_2
        self.line_form.product_qty = 2
        self.assertEqual(self.line_form.price_unit, 30)
        self.assertEqual(self.line_form.price_subtotal, 60)
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)
        self.line_form.product_qty = 1
        self.assertEqual(self.line_form.price_unit, 30)
        self.assertEqual(self.line_form.price_subtotal, 30)
