# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

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
        cls.product_id2 = cls.env["product.template"].create(
            {
                "name": "Test Manufacturer",
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

    def test_sale_order_with_multiple_manufacturer(self):
        manufacturer_id1 = self.env.ref("base.res_partner_2")
        manufacturer_id2 = self.env.ref("base.res_partner_18")
        self.product_id.write(
            {
                "manufacturer_id": manufacturer_id1.id,
            }
        )
        self.product_id2.write(
            {
                "manufacturer_id": manufacturer_id2.id,
            }
        )
        product_variant_id = self.product_id.product_variant_id
        product_variant_id2 = self.product_id2.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id2.id,
                            "product_uom_qty": 10,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        purchase_ids = sale_order1._get_purchase_orders()
        self.assertEqual(len(purchase_ids), 2)

    def test_sale_order_with_same_manufacturer(self):
        manufacturer_id1 = self.env.ref("base.res_partner_2")
        self.product_id.write(
            {
                "manufacturer_id": manufacturer_id1.id,
            }
        )
        self.product_id2.write(
            {
                "manufacturer_id": manufacturer_id1.id,
            }
        )
        product_variant_id = self.product_id.product_variant_id
        product_variant_id2 = self.product_id2.product_variant_id
        sale_order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product_variant_id2.id,
                            "product_uom_qty": 10,
                        },
                    ),
                ],
            }
        )
        sale_order1.action_confirm()
        purchase_ids = sale_order1._get_purchase_orders()
        self.assertEqual(len(purchase_ids), 1)

    def test_replenishement(self):
        orderpoint_id = self.env["stock.warehouse.orderpoint"].search(
            [("qty_to_order", ">", 0)]
        )
        if orderpoint_id:
            manufacturer_id = self.env.ref("base.res_partner_4")
            partner_id = self.env.ref("base.res_partner_12")
            currency_id = self.env.ref("base.USD")
            product_id = orderpoint_id[0].product_id
            product_id.manufacturer_id = manufacturer_id.id
            product_id.seller_ids = [
                (
                    0,
                    0,
                    {
                        "partner_id": partner_id.id,
                        "price": 100,
                        "currency_id": currency_id.id,
                        "delay": 2,
                    },
                )
            ]
            values = {
                "route_ids": self.env["stock.route"],
                "date_planned": datetime(2024, 8, 26, 12, 0),
                "date_deadline": datetime(2024, 8, 27, 12, 0),
                "warehouse_id": self.env["stock.warehouse"].browse(2),
                "orderpoint_id": self.env["stock.warehouse.orderpoint"].browse(4),
                "group_id": self.env["procurement.group"],
                "supplierinfo_id": self.env["product.supplierinfo"],
                "company_id": self.env["res.company"].browse(2),
                "priority": "0",
                "supplier": self.env["product.supplierinfo"],
                "propagate_cancel": False,
            }
            domain = self.env["stock.rule"]._make_po_get_domain(
                company_id=self.env.company,
                values=values,
                partner=self.env["res.partner"],
            )
            self.assertEqual(
                domain,
                (
                    ("partner_id", "=", False),
                    ("state", "=", "draft"),
                    ("picking_type_id", "=", False),
                    ("company_id", "=", 1),
                    ("user_id", "=", False),
                    ("manufacturer_id", "=", 12),
                ),
            )
