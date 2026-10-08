# Copyright 2026 FactorLibre - Luis Alejandro Sandes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSalePurchaseForceVendorBase


class TestSalePurchaseForceVendorNegativeQty(TestSalePurchaseForceVendorBase):
    """A non-positive line is not a purchase, so it must not register a vendor.

    The base fixture already covers the two relevant shapes: `product_a` has a
    seller for the forced vendor (`vendor_b`) and `product_b` has none.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `product_a` sellers use `min_qty` 1, so add a product whose seller
        # starts at 0 to cover both sides of the `min_qty` filter.
        cls.product_c = cls.env["product.product"].create(
            {
                "name": "Test product C",
                "seller_ids": [
                    (0, 0, {"partner_id": cls.vendor_b.id, "min_qty": 0, "price": 30})
                ],
                "route_ids": [(6, 0, [cls.mto.id, cls.buy.id])],
            }
        )

    def setUp(self):
        super().setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]

    def _line_for(self, product, qty):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": qty})
                ],
            }
        )
        order.order_line.vendor_id = self.vendor_b
        return order.order_line

    def test_01_negative_qty_creates_nothing_when_a_price_exists(self):
        """The whole point: no supplierinfo is created out of a return line."""
        self.sol_a.product_uom_qty = -1
        count_before = self.supplierinfo_model.search_count([])
        values = self.sol_a._prepare_procurement_values()
        self.assertEqual(self.supplierinfo_model.search_count([]), count_before)
        # The key must stay set even when nothing matched: stock.move reads it
        # with direct access and would raise KeyError otherwise. It is empty
        # here because this seller starts at `min_qty` 1 and the lookup asks
        # for 0; the line triggers no purchase, so the value is never used.
        self.assertIn("supplierinfo_id", values)
        self.assertFalse(values["supplierinfo_id"])

    def test_02_negative_qty_still_matches_a_seller_starting_at_zero(self):
        line = self._line_for(self.product_c, -1)
        count_before = self.supplierinfo_model.search_count([])
        values = line._prepare_procurement_values()
        self.assertEqual(self.supplierinfo_model.search_count([]), count_before)
        self.assertEqual(values["supplierinfo_id"], self.product_c.seller_ids)

    def test_03_negative_qty_creates_nothing_without_any_price(self):
        self.assertNotIn(self.vendor_b, self.product_b.seller_ids.mapped("partner_id"))
        self.sol_b.product_uom_qty = -1
        count_before = self.supplierinfo_model.search_count([])
        values = self.sol_b._prepare_procurement_values()
        self.assertEqual(self.supplierinfo_model.search_count([]), count_before)
        self.assertIn("supplierinfo_id", values)
        self.assertFalse(values["supplierinfo_id"])

    def test_04_positive_qty_still_creates_the_supplierinfo(self):
        self.assertNotIn(self.vendor_b, self.product_b.seller_ids.mapped("partner_id"))
        count_before = self.supplierinfo_model.search_count([])
        values = self.sol_b._prepare_procurement_values()
        self.assertEqual(self.supplierinfo_model.search_count([]), count_before + 1)
        self.assertEqual(values["supplierinfo_id"].partner_id, self.vendor_b)

    def test_05_positive_qty_still_reuses_the_existing_supplierinfo(self):
        count_before = self.supplierinfo_model.search_count([])
        values = self.sol_a._prepare_procurement_values()
        self.assertEqual(self.supplierinfo_model.search_count([]), count_before)
        expected = self.product_a.seller_ids.filtered(
            lambda x: x.partner_id == self.vendor_b
        )
        self.assertEqual(values["supplierinfo_id"], expected)
