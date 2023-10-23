# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import Form

from odoo.addons.purchase_receipt_expectation_manual.tests.test_purchase_receipt_expectation_manual import (  # noqa: B950
    TestPurchaseReceiptExpectationManual,
)


class TestPurchaseReceiptExpectationManualSplit(TestPurchaseReceiptExpectationManual):
    def test_00_manual_split_receipt_total(self):
        """Tests manual workflow for total receipt

        Steps:
            - Create a PO with `receipt_expectation` set to "manual"
            - Confirm it
            - Check that no picking has been created
            - Create a wizard with scheduled date = tomorrow and:
                1 line where qty = 120, UoM = unit, unit price = 10
            - Run checks on wizard
            - Try to confirm wizard
            - Check picking data
            - Check that a split PO line has been created from the original line

        Expect:
            - No picking is created at PO confirm
            - Pickings' data should match wizards' data
            - Stock moves' data should match wizard lines' data
        """
        self.current_order = self._create_and_check_manual_receipt_order()
        pol = self.current_order.order_line[0]
        wiz = self.current_order._prepare_manual_receipt_wizard()
        self.assertEqual(len(wiz.line_ids), 1)
        tomorrow = datetime.now() + timedelta(days=1)
        with Form(wiz) as wiz_form:
            # Update scheduled date to `tomorrow`
            wiz_form.scheduled_date = tomorrow
            # Update lines: set 1 line with 120 units
            with wiz_form.line_ids.edit(0) as wiz_line:
                wiz_line.qty = 120
                wiz_line.uom_id = self.env.ref("uom.product_uom_unit")
                wiz_line.unit_price = 10
        wiz = self._button_wiz_checks_success(wiz_form.save())
        picking = self._button_wiz_confirm_success(wiz)
        self._check_picking(
            picking,
            expected_picking_data=[
                ("id", self.current_order.picking_ids.ids[-1]),
                ("state", "assigned"),
                ("scheduled_date", tomorrow),
            ],
            expected_move_lines_data=[
                (0, "product_id", pol.product_id),
                (0, "price_unit", 10),
                (0, "product_uom_qty", 120),
                (0, "product_uom", self.env.ref("uom.product_uom_unit")),
            ],
        )
        self.assertEqual(len(self.current_order.order_line), 2)
        self.assertEqual(
            (self.current_order.order_line - pol).manually_split_from_line_id, pol
        )

    def test_01_manual_split_cancel_picking(self):
        """Tests picking cancellation for manual receipt

        Steps:
            - Execute `test_00_manual_split_receipt_total()`
            - Retrieve the test's order
            - Cancel its picking
            - Check order lines

        Expect:
            - The split line shouldn't exist anymore
            - The origin line should have its ordered qty reverted
        """
        self.test_00_manual_split_receipt_total()
        split_line = self.current_order.order_line.filtered(
            "manually_split_from_line_id"
        )
        orig_line = split_line.manually_split_from_line_id
        self.current_order.picking_ids.action_cancel()
        self.assertFalse(split_line.exists())
        self.assertTrue(orig_line.exists())
        self.assertEqual(orig_line.product_qty, orig_line.product_qty_pre_split)

    def test_02_manual_split_cancel_partial_picking_backorder(self):
        """Tests backorder picking cancellation for manual receipt

        Steps:
            - Execute `test_00_manual_split_receipt_total()`
            - Retrieve the test's order
            - Partially receive the picking (with backorder)
            - Cancel the backorder picking
            - Check order lines

        Expect:
            - The unreceived quantity should go back to the origin
        """
        self.test_00_manual_split_receipt_total()
        split_line = self.current_order.order_line.filtered(
            "manually_split_from_line_id"
        )
        orig_line = split_line.manually_split_from_line_id
        picking = self.current_order.picking_ids
        picking.action_set_quantities_to_reservation()
        picking.move_lines.move_line_ids[0].qty_done = 60.0
        picking._action_done()
        backorder = self.current_order.picking_ids - picking
        backorder.action_cancel()
        self.assertTrue(split_line.exists())
        self.assertTrue(orig_line.exists())
        self.assertEqual(orig_line.product_qty, 5.0)
        self.assertEqual(split_line.product_qty, 60.0)

    def test_03_manual_split_cancel_partial_picking(self):
        """Tests backorder picking cancellation for manual receipt

        Steps:
            - Execute `test_00_manual_split_receipt_total()`
            - Retrieve the test's order
            - Partially receive the picking (no backorder)
            - Cancel the backorder picking
            - Check order lines

        Expect:
            - The unreceived quantity should go back to the origin
        """
        self.test_00_manual_split_receipt_total()
        split_line = self.current_order.order_line.filtered(
            "manually_split_from_line_id"
        )
        orig_line = split_line.manually_split_from_line_id
        picking = self.current_order.picking_ids
        picking.action_set_quantities_to_reservation()
        picking.move_lines.move_line_ids[0].qty_done = 60.0
        picking.with_context(cancel_backorder=True)._action_done()
        self.assertTrue(split_line.exists())
        self.assertTrue(orig_line.exists())
        self.assertEqual(orig_line.product_qty, 5.0)
        self.assertEqual(split_line.product_qty, 60.0)
