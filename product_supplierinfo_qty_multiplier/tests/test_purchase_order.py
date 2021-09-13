# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, common


class TestPurchaseOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Supplier test"})
        cls.product_a = cls.env["product.product"].create({"name": "Product A"})
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product A",
                "seller_ids": [
                    (
                        0,
                        False,
                        {
                            "name": cls.partner.id,
                            "min_qty": 1,
                            "multiplier_qty": 2,
                            "price": 100,
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
