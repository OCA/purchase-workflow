# Copyright 2015-17 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductSupplierCodePurchase(TransactionCase):
    def setUp(self):
        super(TestProductSupplierCodePurchase, self).setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.supplier = self.env["res.partner"].create(
            {
                "name": "name",
                "email": "example@yourcompany.com",
                "phone": 123456,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        self.seller = self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_code": "00001",
                "price": 100.0,
            }
        )
        self.purchase_model = self.env["purchase.order"]

    def test_product_supplier_code_purchase(self):
        purchase_order = self.purchase_model.create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.standard_price,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        purchase_order.order_line._onchange_product_code()
        self.assertEqual(
            purchase_order.order_line[0].product_supplier_code,
            "00001",
            "Wrong supplier code",
        )

    def test_supplierinfo_update(self):
        new_product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        purchase_order = self.purchase_model.create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": new_product.id,
                            "product_uom": new_product.uom_id.id,
                            "price_unit": new_product.standard_price,
                            "name": new_product.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_supplier_code": "01000",
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.assertEqual(
            new_product.seller_ids[0].product_code, "01000", "Wrong supplier code"
        )
