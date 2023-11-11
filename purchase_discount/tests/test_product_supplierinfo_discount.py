# Copyright 2018 GRAP - Sylvain Legal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestProductSupplierinfoDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.supplierinfo_model = cls.env["product.supplierinfo"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.partner_3 = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_6")
        cls.supplierinfo = cls.supplierinfo_model.create(
            {
                "min_qty": 0.0,
                "partner_id": cls.partner_3.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "discount": 10,
            }
        )
        cls.supplierinfo2 = cls.supplierinfo_model.create(
            {
                "min_qty": 10.0,
                "partner_id": cls.partner_3.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "discount": 20,
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {"partner_id": cls.partner_3.id}
        )
        cls.po_line_1 = cls.purchase_order_line_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 1.0,
                "product_uom": cls.env.ref("uom.product_uom_categ_unit").id,
                "price_unit": 10.0,
            }
        )

    def test_001_purchase_order_partner_3_qty_1(self):
        purchase_form = Form(self.purchase_order)
        with purchase_form.order_line.edit(0) as line:
            line.product_qty = 1.0
            self.assertEqual(
                line.discount,
                10,
                "Incorrect discount for product 6 with partner 3 and qty 1: "
                "Should be 10%",
            )

    def test_002_purchase_order_partner_3_qty_10(self):
        purchase_form = Form(self.purchase_order)
        with purchase_form.order_line.edit(0) as line:
            line.product_qty = 10.0
            self.assertEqual(
                line.discount,
                20.0,
                "Incorrect discount for product 6 with partner 3 and qty 10: "
                "Should be 20%",
            )

    def test_003_purchase_order_partner_1_qty_1(self):
        purchase_form = Form(self.purchase_order)
        purchase_form.partner_id = self.partner_1
        with purchase_form.order_line.edit(0) as line:
            line.product_qty = 1
            self.assertEqual(
                line.discount,
                0.0,
                "Incorrect discount for product 6 with partner 1 and qty 1",
            )

    def test_004_prepare_purchase_order_line(self):
        res = self.purchase_order_line_model._prepare_purchase_order_line(
            self.product,
            50,
            self.env.ref("uom.product_uom_unit"),
            self.env.ref("base.main_company"),
            self.supplierinfo,
            self.purchase_order,
        )
        self.assertTrue(res.get("discount"), "Should have a discount key")

    def test_005_default_supplierinfo_discount(self):
        # Create an original supplierinfo
        supplierinfo = self.supplierinfo_model.create(
            {
                "min_qty": 0.0,
                "partner_id": self.partner_3.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "discount": 10,
            }
        )
        # Change the partner and raise onchange function
        self.partner_1.default_supplierinfo_discount = 15
        with Form(supplierinfo) as supplierinfo_form:
            supplierinfo_form.partner_id = self.partner_1
            self.assertEqual(
                supplierinfo_form.discount,
                15,
                "Incorrect discount for supplierinfo "
                " after changing partner that has default discount defined.",
            )

    def test_006_supplierinfo_from_purchaseorder(self):
        """Include discount when creating new sellers for a product"""
        partner = self.env.ref("base.res_partner_3")
        product = self.env.ref("product.product_product_8")
        self.assertFalse(
            self.supplierinfo_model.search(
                [
                    ("partner_id", "=", partner.id),
                    ("product_tmpl_id", "=", product.product_tmpl_id.id),
                ]
            )
        )
        order = self.env["purchase.order"].create({"partner_id": partner.id})
        self.purchase_order_line_model.create(
            {
                "date_planned": fields.Datetime.now(),
                "discount": 40,
                "name": product.name,
                "price_unit": 10.0,
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom": product.uom_po_id.id,
                "order_id": order.id,
            }
        )
        order.button_confirm()
        seller = self.supplierinfo_model.search(
            [
                ("partner_id", "=", partner.id),
                ("product_tmpl_id", "=", product.product_tmpl_id.id),
            ]
        )
        self.assertTrue(seller)
        self.assertEqual(seller.discount, 40)

    def test_007_change_price_unit_autoupdate_stock_move(self):
        partner = self.env.ref("base.res_partner_3")
        product = self.env.ref("product.product_product_8")
        order = self.env["purchase.order"].create({"partner_id": partner.id})
        self.purchase_order_line_model.create(
            {
                "date_planned": fields.Datetime.now(),
                "discount": 40,
                "name": product.name,
                "price_unit": 10.0,
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom": product.uom_po_id.id,
                "order_id": order.id,
            }
        )
        order.button_confirm()
        self.assertEqual(order.order_line.move_ids.price_unit, 6)
        order.order_line.price_unit = 100
        self.assertEqual(order.order_line.move_ids.price_unit, 60)
