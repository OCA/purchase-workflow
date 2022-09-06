from odoo import exceptions
from odoo.tests import tagged

from .common import SupplierInfoCommon


@tagged("post_install", "-at_install")
class TestSupplierInfo(SupplierInfoCommon):
    """
    TEST 1 - Check if action is available to the supplier
    TEST 2 - Action has the correct structure
    """

    # TEST 1 - Check if action is available to the supplier
    def test_action_available_to_supplier(self):
        """Check if action is available to the supplier"""
        with self.assertRaises(exceptions.UserError):
            self.product_supplier_info.action_open_component_view()

        self.product_product_toolbox.use_product_components = True

        action = self.product_supplier_info.action_open_component_view()
        self.assertTrue(isinstance(action, dict), msg="Action must be dict type")

    # TEST 2 - Action has the correct structure
    def test_correct_action_structure(self):
        """Action has the correct structure"""
        self.product_product_toolbox.use_product_components = True

        action = self.product_supplier_info.action_open_component_view()
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
            "product.supplierinfo",
            msg="Res Model must be equal to 'product.supplierinfo'",
        )
        self.assertEqual(
            action.get("res_id"),
            self.product_supplier_info.id,
            msg="Res Id must be equal to {}".format(self.product_supplier_info),
        )
        view_id = self.ref(self.view_name)
        self.assertEqual(
            action.get("view_id"),
            view_id,
            msg="View id must be equal to {}".format(view_id),
        )
        self.assertEqual(
            action.get("target"), "new", msg="Target must be equal to 'new'"
        )
