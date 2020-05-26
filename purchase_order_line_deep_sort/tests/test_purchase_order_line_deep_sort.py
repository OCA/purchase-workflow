# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import common


class TestPurchaseOrderLineDeepSort(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        po_model = cls.env["purchase.order"]
        cls.po_line_model = cls.env["purchase.order.line"]
        cls.product_obj = cls.env["product.product"]
        cls.product_1 = cls.product_obj.create(
            {"name": "Test product 1", "default_code": "CDE", "standard_price": 7.5}
        )
        cls.product_2 = cls.product_obj.create(
            {"name": "Test product 2", "default_code": "BCD", "standard_price": 7.3}
        )
        cls.product_3 = cls.product_obj.create(
            {"name": "Test product 3", "default_code": "ABC", "standard_price": 7.4}
        )
        supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.po = po_model.create({"partner_id": supplier.id})
        cls.po_line_1 = cls.po_line_model.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product_1.id,
                "date_planned": "2018-11-01",
                "name": "Test 1",
                "product_qty": 3.0,
                "product_uom": cls.product_1.uom_id.id,
                "price_unit": 10.0,
            }
        )
        cls.po_line_2 = cls.po_line_model.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product_2.id,
                "date_planned": "2018-11-05",
                "name": "Test 2",
                "product_qty": 4.0,
                "product_uom": cls.product_2.uom_id.id,
                "price_unit": 6.0,
            }
        )
        cls.po_line_3 = cls.po_line_model.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product_3.id,
                "date_planned": "2018-11-03",
                "name": "Test 3",
                "product_qty": 2.0,
                "product_uom": cls.product_3.uom_id.id,
                "price_unit": 3.0,
            }
        )

    def _check_value(self, lines, value1, value2):
        self.assertEqual(lines[0].product_id, value1)
        self.assertEqual(lines[2].product_id, value2)

    def test_without_line_order(self):
        self.assertEqual(self.po.order_line[0].product_id, self.product_1)
        self.assertEqual(self.po.order_line[2].product_id, self.product_3)

    def test_line_by_name(self):
        """ Test if lines are ordered by purchase line name"""
        self.po.write({"line_order": "name", "line_direction": "asc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_1, self.product_3)
        self.assertEqual(lines[1].name, "Test 2")
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_3, self.product_1)
        self.assertEqual(lines[1].name, "Test 2")

    def test_line_by_product_name(self):
        """ Test if lines are ordered by product name"""
        self.po.write({"line_order": "product_id.name", "line_direction": "asc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_1, self.product_3)
        self.assertEqual(lines[1].product_id.name, "Test product 2")
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search(
            [("order_id", "=", self.po.id)], order="sequence"
        )
        self._check_value(lines, self.product_3, self.product_1)
        self.assertEqual(lines[1].product_id.name, "Test product 2")

    def test_line_by_product_code(self):
        """ Test if lines are ordered by product code"""
        self.po.write(
            {"line_order": "product_id.default_code", "line_direction": "asc"}
        )
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_3, self.product_1)
        self.assertEqual(lines[1].product_id.default_code, "BCD")
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_1, self.product_3)
        self.assertEqual(lines[1].product_id.default_code, "BCD")

    def test_line_by_date_planned(self):
        """ Test if lines are ordered by purchase line date planned"""
        self.po.write({"line_order": "date_planned", "line_direction": "asc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_1, self.product_2)
        self.assertEqual(fields.Date.to_string(lines[1].date_planned), "2018-11-03")
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_2, self.product_1)
        self.assertEqual(fields.Date.to_string(lines[1].date_planned), "2018-11-03")

    def test_line_by_price_unit(self):
        """ Test if lines are ordered by purchase line price"""
        self.po.write({"line_order": "price_unit", "line_direction": "asc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_3, self.product_1)
        self.assertAlmostEqual(lines[1].price_unit, 6.0)
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_1, self.product_3)
        self.assertAlmostEqual(lines[1].price_unit, 6.0)

    def test_line_by_product_qty(self):
        """ Test if lines are ordered by purchase line product_qty"""
        self.po.write({"line_order": "product_qty", "line_direction": "asc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_3, self.product_2)
        self.assertAlmostEqual(lines[1].product_qty, 3.0)
        self.po.write({"line_direction": "desc"})
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self._check_value(lines, self.product_2, self.product_3)
        self.assertAlmostEqual(lines[1].product_qty, 3.0)

    def test_product_sort_false_values(self):
        """
        Test purchase order lines sorted lines with False values and
        string values (default_code).
        Test sort lines with numeric values with False values
        """
        self.product_2.default_code = False
        self.po.write(
            {"line_order": "product_id.default_code", "line_direction": "asc"}
        )
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self.assertEqual(lines[0].product_id, self.product_2)
        self.po.write({"line_order": "price_unit", "line_direction": "asc"})
        self.po_line_3.price_unit = 0.0
        lines = self.po_line_model.search([("order_id", "=", self.po.id)])
        self.assertEqual(lines[0], self.po_line_3)

    def test_res_config_settings(self):
        purchase_config = (
            self.env["res.config.settings"]
            .sudo()
            .create(
                {"po_line_order_default": "name", "po_line_direction_default": "asc"}
            )
        )
        purchase_config.po_line_order_default = False
        purchase_config.onchange_po_line_order_default()
        self.assertFalse(purchase_config.po_line_direction_default)
