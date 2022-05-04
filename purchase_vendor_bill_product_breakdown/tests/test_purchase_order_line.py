from odoo.tests import common


class TestPurchaseOrderLine(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderLine, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductProduct = self.env["product.product"]
        ProductSupplierInfo = self.env["product.supplierinfo"]
        PurchaseOrder = self.env["purchase.order"]

        uom_unit_id = self.ref("uom.product_uom_unit")
        currency_id = self.env.ref("base.EUR").id

        self.res_partner_test = ResPartner.create({"name": "Test Partner #1"})
        self.res_partner_test_bill_components = ResPartner.create(
            {"name": "Test Partner #2", "bill_components": True}
        )

        self.product_product_test_1 = ProductProduct.create(
            {
                "name": "Test Product #1",
                "standard_price": 100.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_test_2 = ProductProduct.create(
            {
                "name": "Test Product #2",
                "standard_price": 50.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_component_test_1 = ProductProduct.create(
            {
                "name": "Test Component #1",
                "standard_price": 5.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_component_test_2 = ProductProduct.create(
            {
                "name": "Test Component #2",
                "standard_price": 3.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplier_info = ProductSupplierInfo.create(
            {
                "name": self.res_partner_test_bill_components.id,
                "product_id": self.product_product_test_1.id,
                "price": 100,
                "currency_id": currency_id,
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_1.id,
                            "product_uom_qty": 1.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_2.id,
                            "product_uom_qty": 2.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                ],
            }
        )

        self.supplier_partner = ResPartner.create(
            {
                "name": "Partner for Supplier record",
                "bill_components": True,
            }
        )

        self.product_product_test_3 = ProductProduct.create(
            {
                "name": "Test Product #3",
                "standard_price": 100.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_component_test_3 = ProductProduct.create(
            {
                "name": "Test Component #3",
                "standard_price": 1.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_component_test_4 = ProductProduct.create(
            {
                "name": "Test Component #4",
                "standard_price": 5.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_component_test_5 = ProductProduct.create(
            {
                "name": "Test Component #5",
                "standard_price": 6.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplier_info_test = ProductSupplierInfo.create(
            {
                "name": self.supplier_partner.id,
                "product_id": self.product_product_test_3.id,
                "price": 100,
                "currency_id": currency_id,
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_3.id,
                            "product_uom_qty": 3.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_4.id,
                            "product_uom_qty": 4.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_5.id,
                            "product_uom_qty": 5.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                ],
            }
        )

        self.product_product_test_3.write(
            {"seller_ids": [(6, 0, [self.product_supplier_info_test.id])]}
        )

        self.product_product_test_1.write(
            {"seller_ids": [(6, 0, [self.product_supplier_info.id])]}
        )

        self.purchase_order_test_1 = PurchaseOrder.create(
            {
                "partner_id": self.res_partner_test_bill_components.id,
            }
        )
        self.purchase_order_test_1.set_partner_bill_components()

        self.purchase_order_test_2 = PurchaseOrder.create(
            {
                "partner_id": self.res_partner_test.id,
            }
        )
        self.purchase_order_test_2.set_partner_bill_components()

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
