# Copyright 2022 ForgeFlow - David Jiménez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, SavepointCase


class TestPurchaseOrderQtyChange(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "list_price": 25.00, "taxes_id": False}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test Product 2", "list_price": 30.00, "taxes_id": False}
        )
        purchase_form = Form(
            cls.env["purchase.order"].with_context(prevent_onchange_quantity=True)
        )
        purchase_form.partner_id = cls.env.ref("base.res_partner_12")
        with purchase_form.order_line.new() as cls.line_form:
            cls.line_form.product_id = cls.product_1
            cls.line_form.product_qty = 1

    def test_sale_line_misc(self):
        self.assertEqual(self.line_form.price_unit, 0)
        self.assertEqual(self.line_form.price_subtotal, 0)
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 10)
        self.line_form.product_qty = 2
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)
        self.line_form.product_id = self.product_2
        self.assertEqual(self.line_form.price_unit, 0)
        self.assertEqual(self.line_form.price_subtotal, 0)
