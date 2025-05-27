# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchasePackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.line_obj = cls.env["purchase.order.line"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.env.user.groups_id += cls.env.ref("stock.group_adv_location")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.mto_mts_management = True
        cls.route1 = cls.env.ref("stock_mts_mto_rule.route_mto_mts")
        cls.route2 = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.sale_route1 = cls.env["stock.route"].create({"name": "Sale Route1"})
        cls.sale_route2 = cls.env["stock.route"].create({"name": "Sale Route2"})
        cls.vendor_id = cls.env.ref("base.res_partner_12")
        cls.currency_id = cls.env.ref("base.EUR")
        cls.product_id = cls.env["product.template"].create(
            {
                "name": "Test Packaging",
                "sale_ok": True,
                "purchase_ok": True,
                "detailed_type": "product",
                "route_ids": [(6, 0, [cls.route1.id, cls.route2.id])],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.vendor_id.id,
                            "price": 10,
                            "currency_id": cls.currency_id.id,
                            "delay": 1,
                        },
                    )
                ],
            }
        )
        cls.env["res.config.settings"].create(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
                "group_stock_packaging": True,
            }
        ).execute()

    def test_sale_order_with_multiple_route(self):
        product_variant_id = self.product_id.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "route_id": self.sale_route1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "route_id": self.sale_route2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )
        sale_order2.action_confirm()
        purchase_ids1 = sale_order1._get_purchase_orders()
        purchase_ids2 = sale_order2._get_purchase_orders()
        self.assertNotEqual(purchase_ids1.id, purchase_ids2.id)

    def test_sale_order_with_same_route(self):
        product_variant_id = self.product_id.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "route_id": self.sale_route1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "route_id": self.sale_route1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )
        sale_order2.action_confirm()
        purchase_ids1 = sale_order1._get_purchase_orders()
        purchase_ids2 = sale_order2._get_purchase_orders()
        self.assertEqual(purchase_ids1.id, purchase_ids2.id)
