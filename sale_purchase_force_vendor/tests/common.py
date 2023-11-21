# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


class TestSalePurchaseForceVendorBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.vendor_a = cls.env["res.partner"].create({"name": "Test vendor A"})
        cls.vendor_b = cls.env["res.partner"].create({"name": "Test vendor B"})
        cls.mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto.active = True
        cls.buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.buy.sale_selectable = True
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Test product A",
                "seller_ids": [
                    (0, 0, {"partner_id": cls.vendor_a.id, "min_qty": 1, "price": 10}),
                    (0, 0, {"partner_id": cls.vendor_b.id, "min_qty": 1, "price": 20}),
                ],
                "route_ids": [(6, 0, [cls.mto.id, cls.buy.id])],
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Test product B",
                "route_ids": [(6, 0, [cls.mto.id, cls.buy.id])],
            }
        )
        cls.sale_order = cls._create_sale_order(cls)

    def _create_sale_order(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        for product in [self.product_a, self.product_b]:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.vendor_id = self.vendor_b
        return order_form.save()
