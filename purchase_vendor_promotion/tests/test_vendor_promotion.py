# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVendorPromotion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                    "date_start": "2025-01-01",
                    "date_end": "2025-12-31",
                },
                {
                    "partner_id": cls.vendor2.id,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                    "company_id": cls.company_a.id,
                    "min_qty": 1,
                    "price": 120,
                    "is_promotion": True,
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                },
            ]
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
                    "date_start": "2025-01-01",
                }
            )

    def test_purchase_vendor_promotion(self):
        self.env.user.company_id = self.company_a
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor2.id,
                "date_planned": "2024-06-01",
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
        self.assertEqual(orderpoint.promotion_period, "2024-01-01 - 2024-12-31")
