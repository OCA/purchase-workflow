# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, common


class TestPurchaseOrder(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Supplier test"})
        cls.product_a = cls.env["product.product"].create({"name": "Product A"})
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "seller_ids": [
                    (
                        0,
                        False,
                        {
                            "partner_id": cls.partner.id,
                            "min_qty": 1,
                            "multiplier_qty": 2,
                            "price": 100,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "partner_id": cls.partner.id,
                            "min_qty": 100,
                            "multiplier_qty": 2,
                            "price": 95,
                        },
                    ),
                ],
            }
        )

    def _create_purchase_order(self):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product_a
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product_b
        purchase = purchase_form.save()
        purchase.button_confirm()
        return purchase

    def test_purchase_qty_multiplier(self):
        purchase = self._create_purchase_order()
        line_a = purchase.order_line.filtered(lambda x: x.product_id == self.product_a)
        self.assertEqual(line_a.product_qty, 1)
        line_b = purchase.order_line.filtered(lambda x: x.product_id == self.product_b)
        self.assertEqual(line_b.product_qty, 2)

    def test_various_prices(self):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner
        with purchase_form.order_line.new() as line_form_1:
            line_form_1.product_id = self.product_b
            line_form_1.product_qty = 3
        purchase_form.save()
        self.assertEqual(line_form_1.product_qty, 4)
        self.assertEqual(line_form_1.price_unit, 100)

        with purchase_form.order_line.new() as line_form_2:
            line_form_2.product_id = self.product_b
            line_form_2.product_qty = 99
        purchase_form.save()
        self.assertEqual(line_form_2.product_qty, 100)
        self.assertEqual(line_form_2.price_unit, 95)
