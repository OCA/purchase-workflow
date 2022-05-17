from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSupplierInfo(TransactionCase):
    def setUp(self):
        super(TestSupplierInfo, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductSupplierInfo = self.env["product.supplierinfo"]
        ProductProduct = self.env["product.product"]
        uom_unit_id = self.ref("uom.product_uom_unit")
        currency_id = self.env.ref("base.EUR").id

        self.res_partner_test = ResPartner.create(
            {"name": "Test Partner #1", "bill_components": True}
        )

        self.product_product_test_1 = ProductProduct.create(
            {
                "name": "Test Product #1",
                "standard_price": 100.0,
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
                "name": self.res_partner_test.id,
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

    def test_action_open_component_view(self):
        view_id = self.ref(
            "purchase_vendor_bill_product_breakdown.product_supplierinfo_component_form_view"
        )
        action_result = self.product_supplier_info.action_open_component_view()
        self.assertEqual(
            action_result["type"],
            "ir.actions.act_window",
            msg="Action type must be equal 'ir.actions.act_window'",
        )
        self.assertEqual(
            action_result["view_mode"],
            "form",
            msg="Action view mode must be equal 'form'",
        )
        self.assertEqual(
            action_result["res_model"],
            "product.supplierinfo",
            msg="Res Model must be equal 'product.supplierinfo'",
        )
        self.assertEqual(
            action_result["res_id"],
            self.product_supplier_info.id,
            msg="Res Id must be equal {}".format(self.product_supplier_info),
        )
        self.assertEqual(
            len(action_result["views"]), 1, msg="Elements count must be equal 1"
        )
        self.assertEqual(
            len(action_result["views"][0]), 2, msg="Elements count must be equal 2"
        )
        self.assertEqual(
            action_result["views"][0][0],
            view_id,
            msg="View id must be equal {}".format(view_id),
        )
        self.assertEqual(
            action_result["views"][0][1], "form", msg="View type must be equal 'form'"
        )
        self.assertEqual(
            action_result["view_id"],
            view_id,
            msg="View id must be equal {}".format(view_id),
        )
        self.assertEqual(
            action_result["target"], "new", msg="Target must be equal 'new'"
        )
