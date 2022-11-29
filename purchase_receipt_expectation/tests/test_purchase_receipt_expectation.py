# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models
from odoo.tests.common import TransactionCase


class TestPurchaseReceiptExpectation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.po_product = cls.env["product.product"].create(
            {"name": "Product", "detailed_type": "product"}
        )
        cls.po_vals = {
            "partner_id": cls.po_partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.po_product.name,
                        "product_id": cls.po_product.id,
                        "product_qty": 1.0,
                        "product_uom": cls.po_product.uom_po_id.id,
                        "price_unit": 10.0,
                        "date_planned": datetime.today(),
                    },
                )
            ],
        }

    def test_00_automatic_receipt(self):
        """Tests normal workflow when `receipt_expectation == "automatic"`

        Steps:
            - Create a standard purchase order
            - Confirm it

        Expect:
            - `receipt_expectation` must be "automatic" (as default value)
            - At least one picking should have been created
        """
        order = self.env["purchase.order"].create(self.po_vals.copy())
        self.assertEqual(order.receipt_expectation, "automatic")
        order.button_confirm()
        self.assertTrue(order.picking_ids)

    def test_01_custom_receipt(self):
        """Tests workflows with custom receipt expectation values

        Steps:
            - Extend `purchase.order` with a mock-up model
            - Extend `receipt_expectation` with 2 mock-up values,
              "succeeding" and "failing"
            - Create a method related to "succeeding" that simply creates a
              picking (call `_create_picking` with shortcut context key), don't
              create a method for "failing"
            - Create a purchase order with `receipt_expectation = "succeeding"`
            - Create a purchase order with `receipt_expectation = "failing"`
            - Confirm both, one at a time

        Expect:
            - A picking should be created for succeeding order
            - NotImplementedError must be raised when confirming failing order
        """

        class PurchaseOrderMockUp(models.Model):
            _inherit = "purchase.order"

            receipt_expectation = fields.Selection(
                selection_add=[
                    ("succeeding", "Succeeding"),
                    ("failing", "Failing"),
                ],
                ondelete={
                    "succeeding": "set default",
                    "failing": "set default",
                },
            )

            def _create_picking_for_succeeding_receipt_expectation(self):
                """Standard picking creation workflow"""
                orders = self.with_context(skip_custom_receipt_expectation=1)
                return orders._create_picking()

        PurchaseOrderMockUp._build_model(self.registry, self.cr)
        self.registry.setup_models(self.cr)

        succeeding_order = self.env["purchase.order"].create(
            dict(self.po_vals.copy(), receipt_expectation="succeeding")
        )
        self.assertEqual(succeeding_order.receipt_expectation, "succeeding")
        succeeding_order.button_confirm()
        self.assertTrue(succeeding_order.picking_ids)

        failing_order = self.env["purchase.order"].create(
            dict(self.po_vals.copy(), receipt_expectation="failing")
        )
        with self.assertRaises(NotImplementedError) as error:
            failing_order.button_confirm()
        method = "_create_picking_for_failing_receipt_expectation"
        msg = "Method `purchase.order.%s()` not implemented" % method
        self.assertEqual(error.exception.args[0], msg)
