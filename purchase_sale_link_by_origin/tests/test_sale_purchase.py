# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSalePurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.mto_route = cls.env["stock.route"].search(
            [
                ("name", "=", "Replenish on Order (MTO)"),
                "|",
                ("active", "=", False),
                ("active", "=", True),
            ]
        )
        cls.mto_route.active = True
        cls.buy_route = cls.env["stock.route"].search([("name", "=", "Buy")])

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.env["product.product"]
                            .create(
                                {
                                    "name": "Product A",
                                    "list_price": 100,
                                    "seller_ids": [
                                        (
                                            0,
                                            0,
                                            {"partner_id": cls.partner.id, "delay": 5},
                                        )
                                    ],
                                    "route_ids": [
                                        (4, cls.mto_route.id),
                                        (4, cls.buy_route.id),
                                    ],
                                }
                            )
                            .id,
                            "name": "Product A",
                        }
                    )
                ],
            }
        )

    def test_sale_purchase(self):
        self.sale_order.action_confirm()

        purchase_order = self.env["purchase.order"].search(
            [("id", "in", self.sale_order._get_purchase_orders().ids)]
        )

        purchase_order_count_after_confirm = len(self.sale_order._get_purchase_orders())
        sale_order_count_after_confirm = len(purchase_order._get_sale_orders())

        purchase_order.button_cancel()

        purchase_order_count_after_cancel = len(self.sale_order._get_purchase_orders())
        sale_order_count_after_cancel = len(purchase_order._get_sale_orders())

        self.assertEqual(
            purchase_order_count_after_confirm, purchase_order_count_after_cancel
        )
        self.assertEqual(sale_order_count_after_confirm, sale_order_count_after_cancel)
