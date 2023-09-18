# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import Common


class TestPurchaseProductByPackagingOnly(Common):
    def test_write_auto_fill_packaging(self):
        order_line = self.order.order_line
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_qty": 3.0})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        self.product.write({"purchase_only_by_packaging": True})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_qty": self.packaging_tu.qty * 2})
        self.assertTrue(order_line.product_packaging)
        self.assertTrue(order_line.product_packaging_qty)
        self.assertEqual(order_line.product_packaging, self.packaging_tu)
        self.assertEqual(order_line.product_packaging_qty, 2)

        with self.assertRaises(ValidationError):
            order_line.write({"product_packaging": False})

    def test_create_auto_fill_packaging(self):
        """Check when the packaging should be set automatically on the line"""
        # purchase_only_by_packaging is default False
        with Form(self.order) as po:
            with po.order_line.new() as po_line:
                po_line.product_id = self.product
                po_line.product_qty = self.packaging_tu.qty * 2
        po_line = self.order.order_line[-1]
        self.assertFalse(po_line.product_packaging)
        self.assertFalse(po_line.product_packaging_qty)

        # If purchase_only_by_packaging is set, a packaging should be automatically
        # picked if possible
        self.product.purchase_only_by_packaging = True
        with Form(self.order) as po:
            with po.order_line.new() as po_line:
                po_line.product_id = self.product
                po_line.product_qty = self.packaging_tu.qty * 2
        po_line = self.order.order_line[-1]
        self.assertTrue(po_line.product_packaging)
        self.assertTrue(po_line.product_packaging_qty)
        self.assertEqual(po_line.product_packaging, self.packaging_tu)
        self.assertEqual(po_line.product_packaging_qty, 2)

        # If qty does not match a packaging qty, an exception should be raised
        with self.assertRaises(ValidationError):
            with Form(self.order) as po:
                with po.order_line.new() as po_line:
                    po_line.product_id = self.product
                    po_line.product_qty = 2

    @mute_logger("odoo.tests.common.onchange")
    def test_convert_packaging_qty(self):
        """
        Test if the function _convert_packaging_qty is correctly applied
        during po line create/edit and if qties are corrects.
        :return:
        """
        self.product.purchase_only_by_packaging = True
        packaging = self.packaging_tu
        # For this step, the qty is not forced on the packaging po nothing
        # should happens if the qty doesn't match with packaging multiple.
        with Form(self.order) as purchase_order:
            with purchase_order.order_line.edit(0) as po_line:
                po_line.product_packaging = packaging
                po_line.product_qty = 12
                self.assertAlmostEqual(po_line.product_qty, 12, places=self.precision)
                po_line.product_qty = 10
                self.assertAlmostEqual(po_line.product_qty, 10, places=self.precision)
                po_line.product_qty = 36
                self.assertAlmostEqual(po_line.product_qty, 36, places=self.precision)
                po_line.product_qty = 10
                po_line.product_packaging = packaging
        # Now force the qty on the packaging
        packaging.force_purchase_qty = True
        with Form(self.order) as purchase_order:
            with purchase_order.order_line.edit(0) as po_line:
                po_line.product_packaging = packaging
                po_line.product_qty = 50
                self.assertAlmostEqual(po_line.product_qty, 60, places=self.precision)
                po_line.product_qty = 40
                self.assertAlmostEqual(po_line.product_qty, 40, places=self.precision)
                po_line.product_qty = 38
                self.assertAlmostEqual(po_line.product_qty, 40, places=self.precision)
                po_line.product_qty = 22
                self.assertAlmostEqual(po_line.product_qty, 40, places=self.precision)
                po_line.product_qty = 72
                self.assertAlmostEqual(po_line.product_qty, 80, places=self.precision)
                po_line.product_qty = 209.98
                self.assertAlmostEqual(po_line.product_qty, 220, places=self.precision)

    def test_packaging_qty_non_zero(self):
        """Check product packaging quantity.

        The packaging quantity can not be zero.
        """
        self.product.write({"purchase_only_by_packaging": True})
        self.order_line.product_qty = 40  # 2 packs
        with self.assertRaises(ValidationError):
            self.order_line.product_packaging_qty = 0
