from odoo import exceptions
from odoo.tests import Form, tagged

from .common import PurchaseTransactionCase


@tagged("post_install", "-at_install", "test_purchase_order_line")
class TestPurchaseOrderLine(PurchaseTransactionCase):
    """
    TEST 1 - Correct computing supplier for purchase order line
    TEST 2 - Create components for order lines when create purchase order record
    TEST 3 - Check order line has components and activated 'Use Product Component'
    TEST 4 - Correct prepared value for create account move line records
    TEST 5 - Skip records by key 'skip_record'
    TEST 6 - Check if action is available to the order line
    TEST - 7 Components changed when change product id
    """

    # TEST 1 - Correct computing supplier for purchase order line
    def test_check_order_line_supplier(self):
        """Correct computing supplier for purchase order line"""
        with Form(self.purchase_order_test_1) as form:
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_1
                line.price_unit = 50.0
                line.product_qty = 5.0
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_2
                line.price_unit = 40.0
                line.product_qty = 3.0
        line_1, line_2 = self.purchase_order_test_1.order_line
        self.assertEqual(
            self.product_supplier_info,
            line_1.supplier_id,
            msg="Result must be equal to 'product_supplier_info'",
        )
        self.assertFalse(line_2.supplier_id, msg="Result must be False")

    # TEST 2 - Create components for order lines when create purchase order record
    def test_create_and_update_purchase_order_line_components(self):
        """Create components for order lines when create purchase order record"""
        with Form(self.purchase_order_test_1) as form:
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_1
                line.price_unit = 1.0
                line.product_qty = 1.0
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_2
                line.price_unit = 1.0
                line.product_qty = 1.0
        line_1, line_2 = self.purchase_order_test_1.order_line
        self.assertEqual(
            len(line_1.component_ids),
            2,
            msg="Count components must be equal to 2",
        )
        self.assertItemsEqual(
            line_1.component_ids.mapped("component_id"),
            self.product_supplier_info.component_ids.mapped("component_id"),
            msg="Components must be the same",
        )
        self.assertFalse(line_2.component_ids, msg="Recordset must be empty")

        line = self.purchase_order_without_components.order_line
        self.assertFalse(line.component_ids, msg="Components recordset must be empty")

    # TEST 3 - Check order line has components and activated 'Use Product Component'
    def test_has_components(self):
        """Check order line has components and activated 'Use Product Component'"""
        with Form(self.purchase_order_test_1) as form:
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_1
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_2
        line_1, line_2 = self.purchase_order_test_1.order_line
        self.assertTrue(line_1._has_components(), msg="Result must be True")
        self.assertFalse(line_2._has_components(), msg="Result must be False")

        with Form(self.purchase_order_test_2) as form:
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_1
            with form.order_line.new() as line:
                line.product_id = self.product_product_test_2
        line_1, line_2 = self.purchase_order_test_2.order_line
        self.assertFalse(line_1._has_components(), msg="Result must be False")
        self.assertFalse(line_2._has_components(), msg="Result must be False")

    # TEST 4 - Correct prepared value for create account move line records
    def test_prepare_component_account_move_line(self):
        """Correct prepared value for create account move line records"""
        with Form(self.purchase_order_test_1) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 4.0
            line.product_qty = 4.0
        line = self.purchase_order_test_1.order_line
        line.component_ids.write({"qty_to_invoice": 1.0})
        account_move_lines = line._prepare_component_account_move_line()
        self.assertEqual(
            len(account_move_lines), 2, msg="Count elements must be equal to 2"
        )
        product_1, product_2 = list(
            map(lambda l: l[-1].get("product_id"), account_move_lines)
        )

        self.assertEqual(
            self.product_product_component_test_1.id,
            product_1,
            msg="Product id must be equal to '{}'".format(product_1),
        )
        self.assertEqual(
            self.product_product_component_test_2.id,
            product_2,
            msg="Product id must be equal to '{}'".format(product_2),
        )

    # Skip records by key 'skip_record'
    def test_prepare_account_move_line(self):
        """Skip records by key 'skip_record'"""
        with Form(self.purchase_order_test_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product_product_test_1
                line_1.price_unit = 4.0
                line_1.product_qty = 4.0
            with form.order_line.new() as line_2:
                line_2.product_id = self.product_product_test_2
                line_2.price_unit = 5.0
                line_2.product_qty = 5.0
        line_1, line_2 = self.purchase_order_test_1.order_line

        self.assertTrue(
            "skip_record" in line_1._prepare_account_move_line().keys(),
            msg="Key 'skip_record' must not be contains in result",
        )
        self.assertFalse(
            "skip_record" in line_2._prepare_account_move_line().keys(),
            msg="Key 'skip_record' must be contains in result",
        )

    # TEST 6 - Check if action is available to the order line
    def test_action_open_component_view(self):
        """Check if action is available to the order line"""
        with Form(self.purchase_order_test_1) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 50.0
            line.product_qty = 5.0
        line = self.purchase_order_test_1.order_line
        action = line.action_open_component_view()
        self.assertEqual(
            action.get("type"),
            "ir.actions.act_window",
            msg="Action type must be equal to 'ir.actions.act_window'",
        )
        self.assertEqual(
            action.get("view_mode"),
            "form",
            msg="Action view mode must be equal to 'form'",
        )
        self.assertEqual(
            action.get("res_model"),
            line._name,
            msg="Action res model must be equal to 'purchase.order.line'",
        )
        self.assertEqual(
            action.get("res_id"),
            line.id,
            msg="Action res id must be equal to {}".format(line.id),
        )
        view_id = self.ref(self.component_view)
        self.assertEqual(
            action.get("view_id"),
            view_id,
            msg="Action view id must be equal to {}".format(view_id),
        )
        self.assertEqual(
            action.get("target"), "new", msg="Action target must be equal to 'new'"
        )
        with Form(self.purchase_order_test_1) as form:
            form.use_product_components = False
        with self.assertRaises(exceptions.UserError):
            line.action_open_component_view()

    # TEST - 7 Components changed when change product id
    def test_change_order_line_and_partner(self):
        """Components changed when change product id"""
        with Form(self.purchase_order_test_1) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 4.0
            line.product_qty = 4.0
        line = self.purchase_order_test_1.order_line
        expected_components = line.supplier_id.component_ids.mapped("component_id")
        component_ids = line.component_ids.mapped("component_id")
        self.assertItemsEqual(
            expected_components, component_ids, msg="Components must be the same"
        )

        with Form(self.purchase_order_test_1) as form:
            form.partner_id = self.supplier_partner
            with form.order_line.edit(0) as line:
                line.product_id = self.product_product_test_3
        line = self.purchase_order_test_1.order_line
        expected_components = line.supplier_id.component_ids.mapped("component_id")
        component_ids = line.component_ids.mapped("component_id")
        self.assertItemsEqual(
            expected_components, component_ids, msg="Components must be the same"
        )
