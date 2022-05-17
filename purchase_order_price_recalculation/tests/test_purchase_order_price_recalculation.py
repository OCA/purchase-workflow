# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, common


class TestPurchaseOrderPriceRecalculation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env["res.partner"].create({"name": "Test partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Test partner B"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "seller_ids": [
                    (0, 0, {"name": cls.partner_a.id, "price": 10}),
                    (0, 0, {"name": cls.partner_b.id, "price": 20}),
                ],
            }
        )
        cls.order = cls._create_order(cls, cls.partner_a)

    def _create_order(self, partner):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 1
        return order_form.save()

    def test_order_update_lines_info(self):
        product_line = self.order.order_line
        self.assertEqual(product_line.price_unit, 10)
        # Test form
        order_form = Form(self.order)
        order_form.partner_id = self.partner_b
        # Update partner
        self.order.partner_id = self.partner_b
        self.assertEqual(product_line.price_unit, 10)
        self.order.update_lines_info()
        self.assertEqual(product_line.price_unit, 20)
