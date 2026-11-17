# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.purchase_stock.tests.common import PurchaseTestCommon


@tagged("post_install", "-at_install")
class TestVendorPromotion(PurchaseTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_year = date.today().year
        cls.next_year = date.today().year + 1
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.warehouse_a = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company_a.id)], limit=1
        )
        cls.stock_location_a = cls.warehouse_a.lot_stock_id
        cls.vendor1 = (
            cls.env["res.partner"]
            .with_company(cls.company_a)
            .create({"name": "Vendor 1"})
        )
        cls.vendor2 = (
            cls.env["res.partner"]
            .with_company(cls.company_a)
            .create({"name": "Vendor 2"})
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "consu",
            }
        )
        cls.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": cls.vendor1.id,
                    "company_id": cls.company_a.id,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                    "min_qty": 1,
                    "price": 100,
                    "date_start": date(cls.next_year, 1, 1),
                    "date_end": date(cls.next_year, 12, 31),
                },
                {
                    "partner_id": cls.vendor2.id,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                    "company_id": cls.company_a.id,
                    "min_qty": 1,
                    "price": 120,
                    "is_promotion": True,
                    "date_start": date(cls.current_year, 1, 1),
                    "date_end": date(cls.current_year, 12, 31),
                },
            ]
        )
        cls.buy_route = cls.env.ref(
            "purchase_stock.route_warehouse0_buy", raise_if_not_found=False
        )
        cls.test_orderpoint = (
            cls.env["stock.warehouse.orderpoint"]
            .with_company(cls.company_a)
            .create(
                {
                    "product_id": cls.product.id,
                    "product_min_qty": 1,
                    "route_id": cls.buy_route.id,
                }
            )
        )

    def test_promotion_dates_validation(self):
        with self.assertRaises(ValidationError):
            self.env["product.supplierinfo"].create(
                {
                    "partner_id": self.vendor1.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "min_qty": 1,
                    "price": 100,
                    "is_promotion": True,
                    "date_start": date(self.next_year, 1, 1),
                }
            )

    def test_purchase_vendor_promotion(self):
        self.env.user.company_id = self.company_a
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor2.id,
                "date_planned": date(self.current_year, 6, 1),
                "company_id": self.company_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(purchase_order.order_line.price_unit, 120)
        self.assertTrue(purchase_order.order_line.is_promotion)

    def test_orderpoint_promotion(self):
        self.env["stock.warehouse.orderpoint"].search([]).unlink()
        orderpoint = (
            self.env["stock.warehouse.orderpoint"]
            .with_company(self.company_a)
            .create(
                {
                    "product_id": self.product.id,
                    "product_min_qty": 1,
                    "warehouse_id": self.warehouse_a.id,
                    "location_id": self.stock_location_a.id,
                    "supplier_id": self.product.seller_ids[1].id,
                }
            )
        )
        self.assertEqual(
            orderpoint.promotion_period,
            f"{date(self.current_year, 1, 1).strftime('%Y-%m-%d')}"
            " - "
            f"{date(self.current_year, 12, 31).strftime('%Y-%m-%d')}",
        )

    def test_default_supplier_01(self):
        """Assign promotion supplier, even if his price is not the best"""
        default_vendor = self.product.seller_ids.filtered(
            lambda x: x.partner_id == self.vendor2
        )
        self.assertEqual(self.test_orderpoint.supplier_id, default_vendor)

        # If promotion is in the future, consider it as active too
        default_vendor.date_end = (
            f"{date(self.current_year + 1, 12, 31).strftime('%Y-%m-%d')}"
        )
        default_vendor.date_start = (
            f"{date(self.current_year + 1, 1, 1).strftime('%Y-%m-%d')}"
        )
        self.assertEqual(self.test_orderpoint.supplier_id, default_vendor)

    def test_default_supplier_02(self):
        """If no promotion supplier in the product, assign first vendor as default supplier"""
        promotion_vendor = self.product.seller_ids.filtered(
            lambda x: x.partner_id == self.vendor2
        )
        promotion_vendor.write({"is_promotion": False})
        self.assertTrue(self.test_orderpoint.supplier_id)
