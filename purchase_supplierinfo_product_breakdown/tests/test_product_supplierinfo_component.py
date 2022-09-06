from odoo import exceptions
from odoo.tests import Form, tagged

from .common import SupplierInfoCommon


@tagged("post_install", "-at_install")
class TestProductSupplierInfoComponent(SupplierInfoCommon):
    """
    TEST 1 - Checking field values when changing a component
    TEST 2 - Throws an error when Component is not unique or equal to parent product
    """

    # TEST 1 - Checking field values when changing a component
    def test_onchange_components_value(self):
        """Checking field values when changing a component"""
        component = self.product_supplier_info.component_ids[0]
        self.assertEqual(
            component.component_id,
            self.product_product_component_hammer,
            msg="Component must be equal to 'Test Component #1'",
        )
        self.assertEqual(
            component.product_uom_qty, 5, msg="Product Qty must be equal to 5"
        )
        with Form(
            self.product_supplier_info, view=self.view_name
        ) as form, form.component_ids.edit(index=0) as comp:
            comp.component_id = self.product_product_component_drill
            self.assertEqual(
                comp.product_uom_qty, 1, msg="Product Qty must be equal to 1"
            )
            self.assertEqual(
                self.product_product_component_drill.uom_id, comp.product_uom_id
            )

    # TEST 2 - Throws an error when Component is not unique or equal to parent product
    def test_component_is_not_unique_or_parent_product(self):
        """Throws an error when Component is not unique or equal to parent product"""
        with self.assertRaises(exceptions.ValidationError):
            with Form(self.product_supplier_info, view=self.view_name) as form:
                with form.component_ids.new() as line:
                    line.component_id = self.product_product_toolbox

        with self.assertRaises(exceptions.ValidationError):
            with Form(self.product_supplier_info, view=self.view_name) as form:
                with form.component_ids.new() as line:
                    line.component_id = self.product_product_component_hammer

        with self.assertRaises(exceptions.ValidationError):
            with Form(
                self.product_supplier_info, view=self.view_name
            ) as form, form.component_ids.edit(index=0) as line:
                line.component_id = self.product_product_component_saw
