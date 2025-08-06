# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
from datetime import timedelta as td

from odoo.tests import common


class TestPoLineOriginalDate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_model = cls.env["purchase.order"]

        cls.vendor_1 = cls.env["res.partner"].create(
            {
                "name": "Vendor 1",
            }
        )
        cls.product_1 = cls.env["product.product"].create({"name": "test"})
        cls.comparison_delta = td(seconds=1)
        cls.today = datetime.today()
        cls.tomorrow = cls.today + td(1)
        cls.day_2 = cls.today + td(2)

    @classmethod
    def create_purchase_order(cls, product, date_planned, qty=10.0):
        return cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "name": product.name,
                            "price_unit": 100.0,
                            "date_planned": date_planned,
                            "product_qty": qty,
                        },
                    )
                ],
            }
        )

    def test_01_original_date_planned_stored(self):
        po = self.create_purchase_order(self.product_1, self.tomorrow)
        self.assertTrue(po.date_planned)
        self.assertFalse(po.original_date_planned)
        line = po.order_line
        self.assertTrue(line.date_planned)
        self.assertFalse(line.original_date_planned)
        po.button_confirm()
        self.assertTrue(po.original_date_planned)
        self.assertEqual(
            po.date_planned.replace(microsecond=0), po.original_date_planned
        )
        self.assertTrue(line.original_date_planned)
        self.assertEqual(line.date_planned, line.original_date_planned)
        line.date_planned = self.day_2
        self.assertAlmostEqual(
            po.original_date_planned, self.tomorrow, delta=self.comparison_delta
        )
        self.assertAlmostEqual(po.date_planned, self.day_2, delta=self.comparison_delta)
        self.assertEqual(line.original_date_planned, self.tomorrow)
        self.assertEqual(line.date_planned, self.day_2)
