# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import Form

from odoo.addons.purchase_receipt_expectation.tests.test_purchase_receipt_expectation import (
    TestPurchaseReceiptExpectation,
)


class TestPurchaseReceiptExpectationManual(TestPurchaseReceiptExpectation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_vals_manual = dict(
            cls.po_vals,
            receipt_expectation="manual",
            order_line=[
                (
                    0,
                    0,
                    dict(
                        cls.po_vals["order_line"][0][-1],
                        # Update the original PO line qty: 10 dozens instead of
                        # 1 unit, 120 as price unit
                        product_qty=10.0,
                        product_uom=cls.env.ref("uom.product_uom_dozen").id,
                        price_unit=120.0,
                    ),
                )
            ],
        )

    def _create_and_check_manual_receipt_order(self, vals: dict = None):
        vals = dict(vals or self.po_vals_manual)
        order = self.env["purchase.order"].create(vals)
        self.assertEqual(order.receipt_expectation, "manual")
        order.button_confirm()
        self.assertEqual(order.incoming_picking_count, 0)
        return order

    def _button_wiz_checks_success(self, wiz):
        wiz.button_check()
        self.assertEqual(wiz.checks_result, "success")
        return wiz

    def _button_wiz_checks_failure(self, wiz):
        wiz.button_check()
        self.assertEqual(wiz.checks_result, "failure")
        return wiz

    def _button_wiz_confirm_success(self, wiz):
        action = wiz.button_confirm()
        self.assertEqual(wiz.checks_result, "success")
        self.assertEqual(action.get("res_model"), "stock.picking")
        self.assertTrue(action.get("res_id"))
        return self.env["stock.picking"].browse(action["res_id"])

    def _button_wiz_confirm_failure(self, wiz):
        action = wiz.button_confirm()
        self.assertEqual(wiz.checks_result, "failure")
        self.assertEqual(
            action.get("res_model"), "purchase.order.manual.receipt.wizard"
        )
        self.assertTrue(action.get("res_id"))
        new_wiz = self.env["purchase.order.manual.receipt.wizard"].browse(
            action["res_id"]
        )
        self.assertEqual(wiz, new_wiz)
        return wiz

    def _check_picking(self, picking, expected_picking_data, expected_move_lines_data):
        for fname, value in expected_picking_data:
            self.assertEqual(picking[fname], value)
        self.assertEqual(
            len(picking.move_lines), max(i + 1 for i, _, _ in expected_move_lines_data)
        )
        for index, fname, value in expected_move_lines_data:
            self.assertEqual(picking.move_lines[index][fname], value)

    def test_00_manual_receipt_total(self):
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

        Expect:
            - No picking is created at PO confirm
            - Pickings' data should match wizards' data
            - Stock moves' data should match wizard lines' data
        """
        order = self._create_and_check_manual_receipt_order()
        pol = order.order_line[0]
        wiz = order._prepare_manual_receipt_wizard()
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
                ("id", order.picking_ids.ids[-1]),
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

    def test_01_manual_receipt_partial(self):
        """Tests manual workflow for partial receipt

        Steps:
            - Create a PO with `receipt_expectation` set to "manual"
            - Confirm it
            - Check that no picking has been created
            - Create a wizard with scheduled date = tomorrow and:
                1 line where qty = 1, UoM = dozen, unit price = 120
                1 line where qty = 6, UoM = unit, unit price = 15
            - Run checks on wizard
            - Try to confirm wizard
            - Check picking data

        Expect:
            - No picking is created at PO confirm
            - Pickings' data should match wizards' data
            - Stock moves' data should match wizard lines' data
        """
        order = self._create_and_check_manual_receipt_order()
        pol = order.order_line[0]
        wiz = order._prepare_manual_receipt_wizard()
        self.assertEqual(len(wiz.line_ids), 1)
        tomorrow = datetime.now() + timedelta(days=1)
        with Form(wiz) as wiz_form:
            # Update scheduled date to `tomorrow`
            wiz_form.scheduled_date = tomorrow
            # Update lines: set 1 line with 1dozen, create 1 line with 6units
            with wiz_form.line_ids.edit(0) as wiz_line:
                wiz_line.qty = 1
            with wiz_form.line_ids.new() as new_wiz_line:
                new_wiz_line.purchase_line_id = order.order_line[0]
                new_wiz_line.qty = 6
                new_wiz_line.uom_id = self.env.ref("uom.product_uom_unit")
                new_wiz_line.unit_price = 15
        wiz = self._button_wiz_checks_success(wiz_form.save())
        picking = self._button_wiz_confirm_success(wiz)
        self._check_picking(
            picking,
            expected_picking_data=[
                ("id", order.picking_ids.ids[-1]),
                ("state", "assigned"),
                ("scheduled_date", tomorrow),
            ],
            expected_move_lines_data=[
                (0, "product_id", pol.product_id),
                (0, "price_unit", 120),
                (0, "product_uom_qty", 1),
                (0, "product_uom", self.env.ref("uom.product_uom_dozen")),
                (1, "product_id", pol.product_id),
                (1, "price_unit", 15),
                (1, "product_uom_qty", 6),
                (1, "product_uom", self.env.ref("uom.product_uom_unit")),
            ],
        )

    def test_02_manual_receipt_failure(self):
        """Tests manual workflow with failing wizard data

        Steps:
            - Create a PO with `receipt_expectation` set to "manual"
            - Confirm it
            - Check that no picking has been created
            - Create a wizard with scheduled date = tomorrow and:
                1 line where qty = 60, UoM = dozen, unit price = 120
                1 line where qty = -1, UoM = unit, unit price = 10
            - Run checks on wizard
            - Try to confirm wizard
            - Remove second line
            - Run checks on wizard
            - Try to confirm wizard again
            - Check picking data

        Expect:
            - No picking is created at PO confirm
            - After first wizard check, result should be a failure
            - After first wizard confirm, no picking is created yet
            - After second wizard check, result should be a failure again
            - After second wizard confirm, picking is created
            - Pickings' data should match wizards' data
            - Stock moves' data should match wizard lines' data
        """
        order = self._create_and_check_manual_receipt_order()
        pol = order.order_line[0]
        wiz = order._prepare_manual_receipt_wizard()
        self.assertEqual(len(wiz.line_ids), 1)
        tomorrow = datetime.now() + timedelta(days=1)
        with Form(wiz) as wiz_form:
            # Update scheduled date to `tomorrow`
            wiz_form.scheduled_date = tomorrow
            # Update lines: set 1 line with 60dozens, create 1 line with -1unit
            with wiz_form.line_ids.edit(0) as wiz_line:
                wiz_line.qty = 60
            with wiz_form.line_ids.new() as new_wiz_line:
                new_wiz_line.purchase_line_id = order.order_line[0]
                new_wiz_line.qty = -1
                new_wiz_line.uom_id = self.env.ref("uom.product_uom_unit")
                new_wiz_line.unit_price = 10
        wiz = self._button_wiz_checks_failure(wiz_form.save())
        wiz = self._button_wiz_confirm_failure(wiz)
        wiz.line_ids[1].unlink()
        wiz = self._button_wiz_checks_failure(wiz)
        picking = self._button_wiz_confirm_success(wiz)
        self._check_picking(
            picking,
            expected_picking_data=[
                ("id", order.picking_ids.ids[-1]),
                ("state", "assigned"),
                ("scheduled_date", tomorrow),
            ],
            expected_move_lines_data=[
                (0, "product_id", pol.product_id),
                (0, "price_unit", 120),
                (0, "product_uom_qty", 60),
                (0, "product_uom", self.env.ref("uom.product_uom_dozen")),
            ],
        )
