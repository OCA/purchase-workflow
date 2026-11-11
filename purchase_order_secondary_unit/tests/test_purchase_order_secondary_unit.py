# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

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
                        "uom_id": cls.product.uom_id.id,
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
            line.uom_id = self.product_uom_gram
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

    def test_purchase_order_keeps_supplier_price_when_secondary_price_rounds(self):
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "name": "unit-900",
                "factor": 0.9,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        self.product.purchase_secondary_uom_id = secondary_unit
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 19.95,
                "min_qty": 0.0,
            }
        )
        purchase_order = Form(self.purchase_order_obj)
        purchase_order.partner_id = self.partner
        with purchase_order.order_line.new() as line:
            line.product_id = self.product
            self.assertEqual(line.secondary_uom_qty, 1.0)
            self.assertAlmostEqual(line.product_qty, 0.9)
            self.assertAlmostEqual(line.secondary_uom_price, 17.96)
            self.assertAlmostEqual(line.price_unit, 19.95)

    def test_prepare_account_move_line_secondary_uom(self):
        line = self.order.order_line
        line.secondary_uom_id = self.secondary_unit
        self.assertNotIn("secondary_uom_id", line._prepare_account_move_line())
        # Simulate account_move_secondary_unit being installed
        aml = self.env["account.move.line"]
        fields_with_secondary = {**aml._fields, "secondary_uom_id": None}
        with patch.object(type(aml), "_fields", fields_with_secondary):
            res = line._prepare_account_move_line()
        self.assertEqual(res["secondary_uom_id"], self.secondary_unit.id)
