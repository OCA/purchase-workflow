# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.tests import Form, tagged

from .common import TestPurchaseSecondaryUnitCommon


@tagged("-at_install", "post_install")
class TestPurchaseOrderSecondaryUnit(TestPurchaseSecondaryUnitCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_obj = cls.env["purchase.order"]
        po_val = {
            "partner_id": cls.partner.id,
            "company_id": cls.env.company.id,
            "order_line": [
                Command.create(
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_qty": 1,
                        "product_uom_id": cls.product.uom_id.id,
                        "price_unit": 1000.00,
                        "date_planned": fields.Datetime.now(),
                    },
                )
            ],
        }
        po = cls.purchase_order_obj.new(po_val)
        po.onchange_partner_id()
        cls.order = cls.purchase_order_obj.create(po._convert_to_write(po._cache))

    def test_purchase_order_01(self):
        purchase_order = Form(self.order)
        with purchase_order.order_line.edit(0) as line:
            # Test _compute product_qty
            line.secondary_uom_id = self.secondary_unit
            line.secondary_uom_qty = 10.0
            self.assertEqual(line.product_qty, 7.0)
            # Test onchange product uom
            line.secondary_uom_qty = 3500.0
            self.assertEqual(line.product_qty, 2450.0)
            line.product_uom_id = self.product_uom_gram
            self.assertEqual(line.product_qty, 2450000.0)
            self.assertEqual(line.secondary_uom_qty, 3500.0)

    def test_purchase_order_02(self):
        purchase_order = Form(self.order)
        with purchase_order.order_line.new() as line_new:
            # Test default purchase order line secondary uom
            line_new.product_id = self.product
            self.assertEqual(line_new.secondary_uom_id, self.secondary_unit)
            self.assertEqual(line_new.secondary_uom_qty, 1.0)
            self.assertAlmostEqual(line_new.product_qty, 0.7, places=2)
            line_new.product_qty = 1
            self.assertEqual(line_new.secondary_uom_qty, 1.43)

    def test_purchase_order_secondary_uom_price(self):
        purchase_order = Form(self.order)
        with purchase_order.order_line.edit(0) as line:
            line.secondary_uom_id = self.secondary_unit
            line.price_unit = 100.0
            # price_unit = 100, factor = 0.7, secondary_uom_price = 70
            self.assertEqual(line.secondary_uom_price, 70.0)

    def test_purchase_order_confirm_creates_supplierinfo_with_secondary_uom(self):
        new_product = self.env["product.product"].create(
            {
                "name": "New Product",
                "uom_id": self.product_uom_kg.id,
            }
        )
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "name": "Case",
                "uom_id": self.product_uom_unit.id,
                "factor": 5.0,
                "product_tmpl_id": new_product.product_tmpl_id.id,
            }
        )
        po = self.purchase_order_obj.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": new_product.id,
                            "product_qty": 10,
                            "product_uom_id": new_product.uom_id.id,
                            "price_unit": 50.0,
                            "secondary_uom_id": secondary_unit.id,
                            "secondary_uom_qty": 2.0,
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        # Check that supplierinfo was created with secondary_uom_id
        supplierinfo = new_product.seller_ids
        self.assertTrue(supplierinfo)
        self.assertEqual(supplierinfo.partner_id, self.partner)
        self.assertEqual(supplierinfo.secondary_uom_id, secondary_unit)
