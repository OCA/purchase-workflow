# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from .common import PurchaseUomDiscreteCommon


class TestPurchaseUomDiscrete(PurchaseUomDiscreteCommon):
    def _create_purchase_line_with_form(self, product, quantity):
        """Create a purchase line through the form to trigger onchanges.

        :param recordset product: product to set on the line.
        :param float quantity: quantity entered by the buyer.
        :return: saved purchase order line.
        """
        with Form(self.env["purchase.order"]) as purchase_form:
            purchase_form.partner_id = self.vendor
            with purchase_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_qty = quantity
        return purchase_form.save().order_line

    def test_00_unit_quantity_rounds_up_to_integer(self):
        """Test Unit quantities round UP to a whole countable quantity."""
        line = self._create_purchase_line_with_form(self.product_unit, 2.1)

        self.assertEqual(line.product_qty, 3.0)

    def test_01_pack_quantity_rounds_up_to_integer(self):
        """Test Unit-reference pack quantities round UP to a whole quantity."""
        line = self._create_purchase_line_with_form(self.product_pack, 2.7)

        self.assertEqual(line.product_uom_id, self.uom_pack_6)
        self.assertEqual(line.product_qty, 3.0)

    def test_02_integer_quantity_is_unchanged(self):
        """Test whole Unit-reference quantities are kept unchanged."""
        line = self._create_purchase_line_with_form(self.product_pack, 3.0)

        self.assertEqual(line.product_qty, 3.0)

    def test_03_continuous_uom_keeps_fractional_quantity(self):
        """Test continuous UoMs keep meaningful fractional quantities."""
        line = self._create_purchase_line_with_form(self.product_kg, 2.5)

        self.assertEqual(line.product_uom_id, self.uom_kg)
        self.assertEqual(line.product_qty, 2.5)

    def test_04_zero_quantity_is_unchanged(self):
        """Test zero quantities are not rounded by the onchange."""
        line = self._create_purchase_line_with_form(self.product_unit, 0.0)

        self.assertEqual(line.product_qty, 0.0)

    def test_05_programmatic_write_is_not_forced(self):
        """Test direct writes are not forced-rounded outside the form onchange."""
        line = self._create_purchase_line_with_form(self.product_unit, 1.0)

        line.write({"product_qty": 2.7})

        self.assertEqual(line.product_qty, 2.7)
