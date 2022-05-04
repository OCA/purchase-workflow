from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestPurchaseOrder(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductProduct = self.env["product.product"]
        ProductSupplierInfo = self.env["product.supplierinfo"]
        uom_unit_id = self.ref("uom.product_uom_unit")
        currency_id = self.env.ref("base.EUR").id

        self.journal_id = (
            self.env["account.journal"]
            .create(
                {
                    "name": "TEST",
                    "type": "purchase",
                    "code": "TEST",
                    "company_id": self.env.user.company_id.id,
                }
            )
            .id
        )

        self.res_partner_test = ResPartner.create({"name": "Test Partner #1"})
        self.res_partner_test_bill_components = ResPartner.create(
            {"name": "Test Partner #2", "bill_components": True}
        )

        self.env["account.journal"].create(
            {
                "name": "Inventory Valuation",
                "type": "general",
                "code": "STJ",
                "company_id": self.env.user.company_id.id,
                "show_on_dashboard": False,
            }
        ).id

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
                            "product_uom_qty": 5.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_2.id,
                            "product_uom_qty": 3.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                ],
            }
        )

        self.product_product_test_1.write(
            {"seller_ids": [(6, 0, [self.product_supplier_info.id])]}
        )

    def test_purchase_order_set_bill_components(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "name": self.product_product_test_1.name,
                            "price_unit": 79.80,
                            "product_qty": 15.0,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(
            order.bill_components, msg="Order Bill Components must be False"
        )
        self.res_partner_test.write({"bill_components": True})
        self.assertFalse(
            order.bill_components, msg="Order Bill Components must be False"
        )
        order.write({"partner_id": self.res_partner_test_bill_components.id})
        order.set_partner_bill_components()
        self.assertTrue(order.bill_components, msg="Order Bill Components must be True")
        self.res_partner_test_bill_components.write({"bill_components": False})
        self.assertTrue(order.bill_components, msg="Order Bill Components must be True")

    def test_prepare_invoice(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test_bill_components.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "name": self.product_product_test_1.name,
                            "price_unit": 500.0,
                            "product_qty": 5.0,
                        },
                    ),
                ],
            }
        )
        order.write({"bill_components": False})
        invoice_vals = order._prepare_invoice()
        self.assertEqual(
            invoice_vals["invoice_line_ids"],
            [],
            msg="Invoice line ids must be empty list",
        )
        order.write({"bill_components": True})
        invoice_vals = order._prepare_invoice()
        self.assertEqual(
            len(invoice_vals["invoice_line_ids"]),
            2,
            msg="Count invoice line must be equal 2",
        )
