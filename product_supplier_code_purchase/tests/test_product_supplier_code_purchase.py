# Copyright 2015-17 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from .. import __manifest__


class TestProductSupplierCodePurchase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.supplier = self.env["res.partner"].create(
            {"name": "name", "email": "example@yourcompany.com", "phone": 123456}
        )
        self.product = self.env["product.product"].create({"name": "Test product"})
        self.seller = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_code": "00001",
                "price": 100.0,
            }
        )
        self.purchase_model = self.env["purchase.order"]

    def _create_order(self, partner, product, **line_values):
        vals = {
            "product_id": product.id,
            "uom_id": product.uom_id.id,
            "price_unit": product.standard_price,
            "name": product.name,
            "date_planned": fields.Datetime.now(),
            "product_qty": 1,
        }
        vals.update(line_values)
        return self.purchase_model.create(
            {"partner_id": partner.id, "order_line": [(0, 0, vals)]}
        )

    def test_manifest_version(self):
        self.assertTrue(__manifest__.__file__.endswith("__manifest__.py"))

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
                            "uom_id": self.product.uom_id.id,
                            "price_unit": self.product.standard_price,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            purchase_order.order_line[0].product_supplier_code,
            "00001",
            "Wrong supplier code",
        )

    def test_supplierinfo_update(self):
        new_product = self.env["product.product"].create({"name": "Test product"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": new_product.id,
                "product_tmpl_id": new_product.product_tmpl_id.id,
                "product_code": "OLD",
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
                            "uom_id": new_product.uom_id.id,
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

    def test_supplier_code_from_template_supplierinfo(self):
        product = self.env["product.product"].create({"name": "Template product"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": "TEMPLATE",
            }
        )
        order = self._create_order(self.supplier, product)
        self.assertEqual(order.order_line.product_supplier_code, "TEMPLATE")

    def test_supplier_code_ignores_other_partner_supplierinfo(self):
        product = self.env["product.product"].create({"name": "Other partner product"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": "OTHER",
            }
        )
        other_partner = self.env["res.partner"].create({"name": "Other supplier"})
        order = self._create_order(other_partner, product)
        self.assertFalse(order.order_line.product_supplier_code)

    def test_confirm_without_supplierinfo(self):
        partner = self.env["res.partner"].create({"name": "No supplier"})
        product = self.env["product.product"].create({"name": "No supplier product"})
        order = self._create_order(partner, product)
        order.button_confirm()
        self.assertNotEqual(order.state, "draft")

    def test_confirm_without_matching_seller(self):
        product = self.env["product.product"].create({"name": "Min qty product"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": "MIN",
                "min_qty": 10.0,
            }
        )
        order = self._create_order(self.supplier, product)
        order.button_confirm()
        self.assertEqual(product.seller_ids.product_code, "MIN")

    def test_confirm_access_error_is_ignored(self):
        product = self.env["product.product"].create({"name": "Access error product"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": "OLD",
            }
        )
        order = self._create_order(self.supplier, product, product_supplier_code="NEW")
        with patch.object(
            type(self.seller), "write", side_effect=AccessError("no access")
        ):
            order.button_confirm()
        self.assertEqual(product.seller_ids.product_code, "OLD")
