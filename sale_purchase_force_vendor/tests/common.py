# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSalePurchaseForceVendorBase(BaseCommon):
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
        order_lines = cls.sale_order.order_line
        cls.sol_a = order_lines.filtered(lambda x: x.product_id == cls.product_a)
        cls.sol_b = order_lines.filtered(lambda x: x.product_id == cls.product_b)

    def _create_sale_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "route_id": self.mto.id,
                            "vendor_id": self.vendor_b.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_b.id,
                            "route_id": self.mto.id,
                            "vendor_id": self.vendor_b.id,
                        }
                    ),
                ],
            }
        )
        return order
