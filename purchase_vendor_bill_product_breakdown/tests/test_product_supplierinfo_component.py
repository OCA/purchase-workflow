from odoo.tests import tagged

from .common import PurchaseTransactionCase


@tagged("post_install", "-at_install")
class TestProductSupplierInfoComponent(PurchaseTransactionCase):
    def test_onchange_component_id(self):
        component = self.product_supplier_info.component_ids[0]
        self.assertEqual(
            component.component_id,
            self.product_product_component_test_1,
            msg="Component must be equal product 'Test Component #1'",
        )
        self.assertEqual(
            component.product_uom_qty, 5, msg="Product Qty must be equal 5"
        )
        component.component_id = self.product_product_component_test_2
        component.onchange_component_id()
        self.assertEqual(
            component.component_id,
            self.product_product_component_test_2,
            msg="Component must be equal product 'Test Component #2'",
        )
        self.assertEqual(
            component.product_uom_qty, 1.0, msg="Product Qty must be equal 1.0"
        )

    def test_onchange_price(self):
        component = self.product_supplier_info.component_ids[0]
        self.assertEqual(component.price, 0.0, msg="Product price must be equal 0.0")
        component.onchange_price()
        self.assertEqual(component.price, 5.0, msg="Product price must be equal 5.0")
        component.component_supplier_id = self.product_supplier_component_test_1_2
        component.onchange_price()
        self.assertEqual(component.price, 6.0, msg="Product price must be equal 6.0")
