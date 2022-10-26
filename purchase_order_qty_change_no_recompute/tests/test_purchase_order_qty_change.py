# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderQtyChange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test supplier"})
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "taxes_id": False,
                "seller_ids": [
                    (0, False, {"name": cls.partner.id, "min_qty": 1, "price": 25.00}),
                ],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "taxes_id": False,
                "seller_ids": [
                    (0, False, {"name": cls.partner.id, "min_qty": 1, "price": 30.00}),
                ],
            }
        )
        purchase_order_form = Form(
            cls.env["purchase.order"].with_context(prevent_onchange_quantity=True)
        )
        purchase_order_form.partner_id = cls.partner
        with purchase_order_form.order_line.new() as cls.line_form:
            cls.line_form.product_id = cls.product_1
            cls.line_form.product_qty = 1

    def test_purchase_line_misc(self):
        self.assertEqual(self.line_form.price_unit, 25)
        self.assertEqual(self.line_form.price_subtotal, 25)
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 10)
        self.line_form.product_qty = 2
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)
        self.line_form.product_id = self.product_2
        self.line_form.product_qty = 2
        self.assertEqual(self.line_form.price_unit, 30)
        self.assertEqual(self.line_form.price_subtotal, 60)
