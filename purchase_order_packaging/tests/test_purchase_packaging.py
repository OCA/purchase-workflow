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
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.packaging_10 = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 10.0}
        )
        cls.packaging_12 = cls.env["product.packaging"].create(
            {"name": "Test packaging 12", "product_id": cls.product.id, "qty": 12.0}
        )
        cls.env.user.groups_id += cls.env.ref("product.group_stock_packaging")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.mto_mts_management = True
        cls.route1 = cls.env.ref("stock_mts_mto_rule.route_mto_mts")
        cls.route2 = cls.env.ref("purchase_stock.route_warehouse0_buy")
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

    def test_purchase_packaging_from_procurement(self):
        # Check of packaging is well passed from procurement to purchase line
        # and does not take default one
        lines_before = self.line_obj.search([])
        self.group = self.env["procurement.group"].create({"name": "Test"})
        self.env["procurement.group"].run(
            [
                self.group.Procurement(
                    self.product,
                    20.0,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Product",
                    "Product",
                    company_id=self.env.company,
                    values={"product_packaging_id": self.packaging},
                )
            ]
        )
        lines_after = self.line_obj.search([]) - lines_before

        self.assertTrue(lines_after.product_packaging_id)
        self.assertEqual(lines_after.product_packaging_id, self.packaging)

    def test_2_packagings_from_procurement(self):
        # Check of packagings is well passed from procurement to purchase lines
        lines_before = self.line_obj.search([])
        procur1 = self.env["procurement.group"].create({"name": "Test1"})
        procur2 = self.env["procurement.group"].create({"name": "Test2"})
        self.env["procurement.group"].run(
            [
                procur1.Procurement(
                    self.product,
                    5.0,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Product",
                    "Product",
                    company_id=self.env.company,
                    values={"product_packaging_id": self.packaging},
                ),
                procur2.Procurement(
                    self.product,
                    24.0,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Product",
                    "Product",
                    company_id=self.env.company,
                    values={"product_packaging_id": self.packaging_12},
                ),
            ]
        )
        lines_after = self.line_obj.search([]) - lines_before
        self.assertEqual(len(lines_after), 2)
        self.assertTrue(lines_after[0].product_packaging_id)
        self.assertTrue(lines_after[1].product_packaging_id)

    def test_purchase_packaging_from_move(self):
        # Check of packaging is well passed from stock move to procurement,
        # then to purchase line and does not take default one
        lines_before = self.line_obj.search([])

        self.move = self.env["stock.move"].create(
            {
                "name": "Product Test",
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 20.0,
                "product_packaging_id": self.packaging.id,
                "procure_method": "make_to_order",
            }
        )

        self.move._action_confirm()

        lines_after = self.line_obj.search([]) - lines_before

        self.assertTrue(lines_after.product_packaging_id)
        self.assertEqual(lines_after.product_packaging_id, self.packaging)

    def test_muti_sale_order_with_packaging(self):
        self.env["res.config.settings"].create(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
                "group_stock_packaging": True,
            }
        ).execute()

        self.product_id.write(
            {
                "packaging_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pack of 6",
                            "qty": 6,
                            "sales": True,
                            "purchase": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "pack of 12",
                            "qty": 12,
                            "sales": True,
                            "purchase": True,
                        },
                    ),
                ],
            }
        )

        product_variant_id = self.product_id.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                0
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 6,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                1
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 12,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        purchase_id = sale_order1._get_purchase_orders()
        self.assertEqual(len(purchase_id.order_line), 2)
        self.assertEqual(purchase_id.order_line[0].product_qty, 6)
        self.assertEqual(purchase_id.order_line[1].product_qty, 12)

        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                1
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 12,
                        },
                    )
                ],
            }
        )
        sale_order2.action_confirm()
        self.assertEqual(len(purchase_id.order_line), 2)
        self.assertEqual(purchase_id.order_line[0].product_qty, 6)
        self.assertEqual(purchase_id.order_line[1].product_qty, 24)

        sale_order3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                1
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                0
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 6,
                        },
                    ),
                ],
            }
        )
        sale_order3.action_confirm()
        self.assertEqual(len(purchase_id.order_line), 2)
        self.assertEqual(purchase_id.order_line[0].product_qty, 12)
        self.assertEqual(purchase_id.order_line[1].product_qty, 36)

    def test_muti_sale_order_without_package(self):
        self.env["res.config.settings"].create(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        ).execute()

        product_variant_id = self.product_id.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 6,
                        },
                    )
                ],
            }
        )
        sale_order1.action_confirm()
        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 12,
                        },
                    )
                ],
            }
        )
        sale_order2.action_confirm()
        purchase_id = sale_order1._get_purchase_orders()
        self.assertEqual(len(purchase_id.order_line), 1)
        self.assertEqual(purchase_id.order_line.product_qty, 18)

    def test_sale_order_with_package_and_with_stock(self):
        self.env["res.config.settings"].create(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
                "group_stock_packaging": True,
            }
        ).execute()

        self.product_id.write(
            {
                "packaging_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pack of 6",
                            "qty": 6,
                            "sales": True,
                            "purchase": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "pack of 12",
                            "qty": 12,
                            "sales": True,
                            "purchase": True,
                        },
                    ),
                ],
            }
        )
        product_variant_id = self.product_id.product_variant_id
        self.env["stock.quant"].create(
            {
                "product_id": product_variant_id.id,
                "quantity": 6,
                "location_id": self.warehouse.lot_stock_id.id,
            }
        )
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                0
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 6,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                1
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 12,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        purchase_id = sale_order1._get_purchase_orders()
        self.assertEqual(product_variant_id.qty_available, 6)
        self.assertEqual(len(purchase_id.order_line), 1)
        self.assertEqual(purchase_id.order_line[0].product_qty, 12)

        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_packaging_id": product_variant_id.packaging_ids[
                                0
                            ].id,
                            "product_packaging_qty": 1,
                            "product_uom_qty": 6,
                        },
                    )
                ],
            }
        )
        sale_order2.action_confirm()
        self.assertEqual(len(purchase_id.order_line), 2)
        self.assertEqual(purchase_id.order_line[0].product_qty, 12)
        self.assertEqual(purchase_id.order_line[1].product_qty, 6)
