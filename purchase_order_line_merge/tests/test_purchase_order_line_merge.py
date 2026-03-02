from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseOrderLineMerge(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test Vendor 2"})
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product A", "type": "consu"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product B", "type": "consu"}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 15%",
                "type_tax_use": "purchase",
                "amount": 15,
            }
        )
        cls.po_1 = cls.env["purchase.order"].create({"partner_id": cls.partner.id})
        cls.po_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 10.0,
                "price_unit": 100.0,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )
        cls.po_line_2 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_qty": 5.0,
                "price_unit": 200.0,
            }
        )
        cls.po_2 = cls.env["purchase.order"].create({"partner_id": cls.partner.id})
        cls.po_line_3 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po_2.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 8.0,
                "price_unit": 100.0,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )

    def _create_wizard(self, line_ids, vals=None):
        ctx = {"active_ids": line_ids, "active_model": "purchase.order.line"}
        wizard = (
            self.env["purchase.order.line.merge"].with_context(**ctx).create(vals or {})
        )
        return wizard

    def test_default_vals(self):
        """Default values: partner and quantity based on source quantity."""
        # Partner auto-filled when all lines share the same vendor
        ctx = {
            "active_ids": (self.po_line_1 | self.po_line_3).ids,
            "active_model": "purchase.order.line",
        }
        defaults = (
            self.env["purchase.order.line.merge"]
            .with_context(**ctx)
            .default_get(["partner_id", "line_ids"])
        )
        self.assertEqual(defaults.get("partner_id"), self.partner.id)
        self.assertEqual(len(defaults.get("line_ids", [])), 2)
        wizard = self._create_wizard(self.po_line_1.ids)
        self.assertEqual(wizard.line_ids.quantity, 10.0)

    def test_default_vals_excludes_canceled_lines(self):
        """Canceled source lines are ignored in wizard initialization."""
        po_canceled = self.env["purchase.order"].create({"partner_id": self.partner.id})
        canceled_line = self.env["purchase.order.line"].create(
            {
                "order_id": po_canceled.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_qty": 2.0,
                "price_unit": 25.0,
            }
        )
        po_canceled.button_cancel()
        wizard = self._create_wizard((self.po_line_1 | canceled_line).ids)
        self.assertEqual(wizard.line_ids.mapped("source_line_id"), self.po_line_1)

    def test_validation_quantity(self):
        """Only checks for at least one positive quantity to merge."""
        # Negative values are ignored by merge selection (quantity > 0)
        wizard = self._create_wizard(self.po_line_1.ids)
        wizard.line_ids.quantity = -1.0
        with self.assertRaisesRegex(
            UserError, r"No lines with quantity greater than zero"
        ):
            wizard.action_merge()
        # All zero
        wizard.line_ids.quantity = 0.0
        with self.assertRaisesRegex(
            UserError, r"No lines with quantity greater than zero"
        ):
            wizard.action_merge()

    def test_validation_order_constraints(self):
        """Order-level validations: currencies, warehouses, and non-draft state."""
        # Different currencies
        currency_eur = self.env.ref("base.EUR")
        po_eur = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "currency_id": currency_eur.id,
            }
        )
        po_line_eur = self.env["purchase.order.line"].create(
            {
                "order_id": po_eur.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_qty": 5.0,
                "price_unit": 50.0,
            }
        )
        wizard = self._create_wizard((self.po_line_1 | po_line_eur).ids)
        with self.assertRaisesRegex(UserError, r"different currencies"):
            wizard.action_merge()
        # Different warehouses
        warehouse_2 = self.env["stock.warehouse"].create(
            {"name": "Warehouse 2", "code": "WH2"}
        )
        po_wh2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": warehouse_2.in_type_id.id,
            }
        )
        po_line_wh2 = self.env["purchase.order.line"].create(
            {
                "order_id": po_wh2.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_qty": 5.0,
                "price_unit": 50.0,
            }
        )
        wizard = self._create_wizard((self.po_line_1 | po_line_wh2).ids)
        with self.assertRaisesRegex(UserError, r"different warehouses"):
            wizard.action_merge()
        # Non-draft order is currently allowed (placeholder hook, no validation yet)
        po_confirmed = self.env["purchase.order"].create(
            {"partner_id": self.partner.id}
        )
        po_line_confirmed = self.env["purchase.order.line"].create(
            {
                "order_id": po_confirmed.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_qty": 5.0,
                "price_unit": 50.0,
            }
        )
        po_confirmed.button_confirm()
        wizard = self._create_wizard(po_line_confirmed.ids)
        result = wizard.action_merge()
        self.assertTrue(self.env["purchase.order"].browse(result["res_id"]).exists())

    def test_merge_basic(self):
        """Basic merge creates a new PO with correct lines."""
        wizard = self._create_wizard(
            (self.po_line_1 | self.po_line_2).ids,
        )
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(len(wizard.line_ids), 2)
        result = wizard.action_merge()
        new_po = self.env["purchase.order"].browse(result["res_id"])
        self.assertTrue(new_po.exists())
        self.assertEqual(new_po.partner_id, self.partner)
        self.assertEqual(len(new_po.order_line), 2)
        line_a = new_po.order_line.filtered(lambda ln: ln.product_id == self.product_1)
        self.assertEqual(line_a.product_qty, 10.0)
        self.assertEqual(line_a.price_unit, 100.0)
        line_b = new_po.order_line.filtered(lambda ln: ln.product_id == self.product_2)
        self.assertEqual(line_b.product_qty, 5.0)
        self.assertEqual(line_b.price_unit, 200.0)

    def test_merge_same_product(self):
        """Same product lines are grouped; origin references source POs."""
        wizard = self._create_wizard(
            (self.po_line_1 | self.po_line_3).ids,
        )
        result = wizard.action_merge()
        new_po = self.env["purchase.order"].browse(result["res_id"])
        # Same product/price/uom/taxes → single line with summed qty
        self.assertEqual(len(new_po.order_line), 1)
        self.assertEqual(new_po.order_line.product_qty, 18.0)
        self.assertEqual(new_po.order_line.price_unit, 100.0)
        # Origin field references both source POs
        self.assertIn(self.po_1.name, new_po.origin)
        self.assertIn(self.po_2.name, new_po.origin)

    def test_merge_same_product_different_discount(self):
        """Same product lines with different discount must not be grouped."""
        self.po_line_1.discount = 5.0
        self.po_line_3.discount = 10.0
        wizard = self._create_wizard((self.po_line_1 | self.po_line_3).ids)
        result = wizard.action_merge()
        new_po = self.env["purchase.order"].browse(result["res_id"])
        self.assertEqual(len(new_po.order_line), 2)
        discounts = sorted(new_po.order_line.mapped("discount"))
        self.assertEqual(discounts, [5.0, 10.0])

    def test_merge_updates_source(self):
        """Merge reduces source qty, cancels empty orders, handles partial."""
        # Full merge: original lines go to zero, order gets cancelled
        wizard = self._create_wizard(
            (self.po_line_1 | self.po_line_2).ids,
        )
        wizard.action_merge()
        self.assertEqual(self.po_line_1.product_qty, 0.0)
        self.assertEqual(self.po_line_2.product_qty, 0.0)
        self.assertEqual(self.po_1.state, "cancel")
        # Partial merge: only moved qty is subtracted
        wizard = self._create_wizard(self.po_line_3.ids)
        wizard.line_ids.quantity = 3.0
        wizard.action_merge()
        self.assertEqual(self.po_line_3.product_qty, 5.0)

    def test_merge_updates_only_filtered_lines(self):
        """Only lines selected for merge update source quantities."""
        wizard = self._create_wizard((self.po_line_1 | self.po_line_2).ids)
        line_1 = wizard.line_ids.filtered(
            lambda ln: ln.source_line_id == self.po_line_1
        )
        line_2 = wizard.line_ids.filtered(
            lambda ln: ln.source_line_id == self.po_line_2
        )
        line_1.quantity = 2.0
        line_2.quantity = -1.0
        wizard.action_merge()
        self.assertEqual(self.po_line_1.product_qty, 8.0)
        self.assertEqual(self.po_line_2.product_qty, 5.0)

    def test_computed_fields(self):
        """Subtotal and editable price behavior."""
        wizard = self._create_wizard(self.po_line_1.ids)
        line = wizard.line_ids
        # Subtotal = quantity * price_unit
        self.assertEqual(line.price_subtotal, line.quantity * 100.0)
        line.quantity = 3.0
        self.assertEqual(line.price_subtotal, 3.0 * 100.0)
        # Editable price updates subtotal
        line.price_unit = 150.0
        self.assertEqual(line.price_subtotal, 3.0 * 150.0)
        # Edited price carries through to the new PO
        result = wizard.action_merge()
        new_po = self.env["purchase.order"].browse(result["res_id"])
        self.assertEqual(new_po.order_line.price_unit, 150.0)

    def test_computed_subtotal_with_discount(self):
        """Subtotal takes the source line discount into account."""
        self.po_line_1.discount = 10.0
        wizard = self._create_wizard(self.po_line_1.ids)
        line = wizard.line_ids
        self.assertEqual(line.discount, 10.0)
        self.assertEqual(line.price_subtotal, 10.0 * 100.0 * 0.9)
        line.quantity = 3.0
        self.assertEqual(line.price_subtotal, 3.0 * 100.0 * 0.9)
        # The discount is carried over to the merged order line
        result = wizard.action_merge()
        new_po = self.env["purchase.order"].browse(result["res_id"])
        self.assertEqual(new_po.order_line.discount, 10.0)
