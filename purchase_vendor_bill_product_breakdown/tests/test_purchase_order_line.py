from odoo.tests import tagged

from .common import PurchaseTransactionCase


@tagged("post_install", "-at_install")
class TestPurchaseOrderLine(PurchaseTransactionCase):
    def test_get_supplier(self):
        PurchaseOrderLine = self.env["purchase.order.line"]

        purchase_order_line_test_1 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": self.product_product_test_1.name,
                "price_unit": 50.0,
                "product_qty": 5.0,
            }
        )

        purchase_order_line_test_2 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_2.id,
                "name": self.product_product_test_2.name,
                "price_unit": 40.0,
                "product_qty": 3.0,
            }
        )

        correct_result = self.product_supplier_info
        result = purchase_order_line_test_1.get_supplier()
        self.assertEqual(
            correct_result, result, msg="Result must be equal 'correct_result'"
        )

        result = purchase_order_line_test_2.get_supplier()
        self.assertEqual(result, False, msg="Result must be False")

    def test_create_and_update_purchase_order_line_components(self):
        PurchaseOrderLine = self.env["purchase.order.line"]

        test_line_with_components = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": "Purchase Order Line with components",
                "price_unit": 1.0,
                "product_qty": 1.0,
            }
        )

        self.assertEqual(
            len(test_line_with_components.component_ids),
            2,
            msg="Count components must be equal 2",
        )
        self.assertEqual(
            len(test_line_with_components.component_ids),
            len(self.product_supplier_info.component_ids),
            msg="Count components must be equal",
        )
        for line in test_line_with_components.component_ids:
            self.assertTrue(
                line.component_id
                in self.product_supplier_info.component_ids.mapped("component_id"),
                msg="Component must be contains in supplierinfo components",
            )

        test_line_without_components = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_2.id,
                "name": "Purchase Order Line without components",
                "price_unit": 1.0,
                "product_qty": 1.0,
            }
        )

        self.assertEqual(
            len(test_line_without_components.component_ids),
            0,
            msg="Count components must be equal 0",
        )

    def test_has_components(self):
        PurchaseOrderLine = self.env["purchase.order.line"]

        test_line_1 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": "Partner with flag Bill Components is True and product with components",
            }
        )

        self.assertTrue(test_line_1._has_components(), msg="Result must be True")

        test_line_2 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_2.id,
                "product_id": self.product_product_test_1.id,
                "name": "Partner with flag "
                "Bill Components is False "
                "and product with components",
            }
        )

        self.assertFalse(test_line_2._has_components(), msg="Result must be False")

        test_line_3 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_2.id,
                "name": "Partner with flag "
                "Bill Components is True "
                "and product without components",
            }
        )

        self.assertFalse(test_line_3._has_components(), msg="Result must be False")

        test_line_4 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_2.id,
                "product_id": self.product_product_test_2.id,
                "name": "Partner with flag "
                "Bill Components is False "
                "and product without components",
            }
        )

        self.assertFalse(test_line_4._has_components(), msg="Result must be False")

    def test_prepare_component_account_move_line(self):
        PurchaseOrderLine = self.env["purchase.order.line"]

        self.purchase_order_test_1.write({"name": "TEST"})

        test_line_1 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": self.product_product_test_1.name,
                "price_unit": 4.0,
                "product_qty": 4.0,
            }
        )
        test_line_1.component_ids.write({"qty_to_invoice": 1.0})

        account_move_lines = test_line_1._prepare_component_account_move_line()

        self.assertEqual(
            len(account_move_lines), 2, msg="Count elements must be equal 2"
        )
        _, _, component_line_one = account_move_lines[0]
        _, _, component_line_two = account_move_lines[1]

        correct_one_name = "TEST: Test Component #1"
        correct_two_name = "TEST: Test Component #2"
        self.assertEqual(
            component_line_one["name"],
            correct_one_name,
            msg="Value must be equal value variable 'correct_one_name'",
        )
        self.assertEqual(
            component_line_two["name"],
            correct_two_name,
            msg="Value must be equal value variable 'correct_two_name'",
        )
        correct_component_id_one = component_line_one["product_id"]
        self.assertEqual(
            self.product_product_component_test_1.id,
            correct_component_id_one,
            msg="Value must be equal value variable 'correct_component_id_one'",
        )
        correct_component_id_two = component_line_two["product_id"]
        self.assertEqual(
            self.product_product_component_test_2.id,
            correct_component_id_two,
            msg="Value must be equal value variable 'correct_component_id_two'",
        )

    def test_prepare_account_move_line(self):
        PurchaseOrderLine = self.env["purchase.order.line"]

        test_line_1 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": self.product_product_test_1.name,
                "price_unit": 4.0,
                "product_qty": 4.0,
            }
        )

        test_line_2 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_2.id,
                "name": self.product_product_test_2.name,
                "price_unit": 5.0,
                "product_qty": 5.0,
            }
        )

        result = test_line_1._prepare_account_move_line()
        self.assertTrue(
            "skip_record" in result.keys(),
            msg="Key 'skip_record' must not be contains in result",
        )

        result = test_line_2._prepare_account_move_line()
        self.assertFalse(
            "skip_record" in result.keys(),
            msg="Key 'skip_record' must be contains in result",
        )

    def test_action_open_component_view(self):
        PurchaseOrderLine = self.env["purchase.order.line"]
        view_id = self.ref(
            "purchase_vendor_bill_product_breakdown.purchase_order_line_components_form_view"
        )
        purchase_order_line_test_1 = PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order_test_1.id,
                "product_id": self.product_product_test_1.id,
                "name": self.product_product_test_1.name,
                "price_unit": 50.0,
                "product_qty": 5.0,
            }
        )
        action = purchase_order_line_test_1.action_open_component_view()
        self.assertEqual(
            action["type"],
            "ir.actions.act_window",
            msg="Action type must be equal 'ir.actions.act_window'",
        )
        self.assertEqual(
            action["view_mode"], "form", msg="Action view mode must be equal 'form'"
        )
        self.assertEqual(
            action["res_model"],
            purchase_order_line_test_1._name,
            msg="Action res model must be equal 'purchase.order.line'",
        )
        self.assertEqual(
            action["res_id"],
            purchase_order_line_test_1.id,
            msg="Action res id must be equal {}".format(purchase_order_line_test_1.id),
        )
        self.assertEqual(
            action["view_id"],
            view_id,
            msg="Action view id must be equal {}".format(view_id),
        )
        self.assertEqual(
            action["target"], "new", msg="Action target must be equal 'new'"
        )

    def test_write(self):
        PurchaseOrderLine = self.env["purchase.order.line"]
        order_id = self.purchase_order_test_1
        order_id.write({"partner_id": self.res_partner_test_bill_components.id})
        line = PurchaseOrderLine.create(
            {
                "order_id": order_id.id,
                "product_id": self.product_product_test_1.id,
                "name": self.product_product_test_1.name,
                "price_unit": 4.0,
                "product_qty": 4.0,
            }
        )
        self.assertEqual(
            len(line.component_ids), 2, msg="Components count must be equal 2"
        )
        component1, component2 = list(line.component_ids)
        self.assertEqual(
            component1.component_id,
            self.product_product_component_test_1,
        )
        self.assertEqual(
            component2.component_id,
            self.product_product_component_test_2,
        )
        order_id.write({"partner_id": self.supplier_partner.id})
        line.write({"product_id": self.product_product_test_3.id})
        self.assertEqual(
            len(line.component_ids), 3, msg="Components count must be equal 3"
        )
        component1, component2, component3 = list(line.component_ids)
        self.assertEqual(
            component1.component_id,
            self.product_product_component_test_3,
        )
        self.assertEqual(
            component2.component_id,
            self.product_product_component_test_4,
        )
        self.assertEqual(
            component3.component_id,
            self.product_product_component_test_5,
        )
