from odoo.tests import TransactionCase


class PurchaseTransactionCase(TransactionCase):
    def setUp(self):
        super(PurchaseTransactionCase, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductProduct = self.env["product.product"]
        ProductSupplierInfo = self.env["product.supplierinfo"]
        PurchaseOrder = self.env["purchase.order"]
        uom_unit_id = self.ref("uom.product_uom_unit")
        currency_id = self.ref("base.EUR")

        self.res_partner_test = ResPartner.create({"name": "Test Partner #1"})
        self.res_partner_test_bill_components = ResPartner.create(
            {"name": "Test Partner #2", "bill_components": True}
        )
        self.res_partner_supplier = ResPartner.create({"name": "Test Partner Supplier"})
        self.res_partner_supplier_2 = ResPartner.create(
            {"name": "Test Partner Supllier #2"}
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

        self.product_supplier_component_test_1 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier.id,
                "product_id": self.product_product_component_test_1.id,
                "price": 5.0,
                "currency_id": currency_id,
            }
        )

        self.product_supplier_component_test_1_2 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier_2.id,
                "product_id": self.product_product_component_test_1.id,
                "price": 6.0,
                "currency_id": currency_id,
            }
        )

        self.product_product_component_test_1.write(
            {
                "seller_ids": [
                    (
                        6,
                        0,
                        [
                            self.product_supplier_component_test_1.id,
                            self.product_supplier_component_test_1_2.id,
                        ],
                    )
                ]
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

        self.product_supplier_component_test_2 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier.id,
                "product_id": self.product_product_component_test_2.id,
                "price": 3.0,
                "currency_id": currency_id,
            }
        )

        self.product_product_component_test_2.write(
            {"seller_ids": [(6, 0, self.product_supplier_component_test_2.ids)]}
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
                            "component_supplier_id": self.product_supplier_component_test_1.id,
                            "product_uom_qty": 5.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_2.id,
                            "component_supplier_id": self.product_supplier_component_test_2.id,
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
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplier_component_test_3 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier.id,
                "product_id": self.product_product_component_test_3.id,
                "price": 1.0,
                "currency_id": currency_id,
            }
        )

        self.product_product_component_test_3.write(
            {"seller_ids": [(6, 0, self.product_supplier_component_test_3.ids)]}
        )

        self.product_product_component_test_4 = ProductProduct.create(
            {
                "name": "Test Component #4",
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplier_component_test_4 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier.id,
                "product_id": self.product_product_component_test_4.id,
                "price": 5.0,
                "currency_id": currency_id,
            }
        )

        self.product_product_component_test_4.write(
            {"seller_ids": [(6, 0, self.product_supplier_component_test_4.ids)]}
        )

        self.product_product_component_test_5 = ProductProduct.create(
            {
                "name": "Test Component #5",
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplier_component_test_5 = ProductSupplierInfo.create(
            {
                "name": self.res_partner_supplier.id,
                "product_id": self.product_product_component_test_5.id,
                "price": 6.0,
                "currency_id": currency_id,
            }
        )

        self.product_product_component_test_5.write(
            {"seller_ids": [(6, 0, self.product_supplier_component_test_5.ids)]}
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
                            "component_supplier_id": self.product_supplier_component_test_3.id,
                            "product_uom_qty": 3.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_4.id,
                            "component_supplier_id": self.product_supplier_component_test_4.id,
                            "product_uom_qty": 4.0,
                            "product_uom_id": uom_unit_id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "component_id": self.product_product_component_test_5.id,
                            "component_supplier_id": self.product_supplier_component_test_5.id,
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
