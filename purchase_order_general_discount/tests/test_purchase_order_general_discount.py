# Copyright 2019 Tecnativa - David Vidal
# Copyright 2022 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import TransactionCase, common


class TestPurchaseOrderLineInput(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "purchase_general_discount": 10.0}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        order_form = common.Form(cls.env["purchase.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom = cls.product.uom_id
            line_form.product_qty = 1
            line_form.price_unit = 1000.00
        cls.order = order_form.save()
        cls.View = cls.env["ir.ui.view"]

    def test_01_default_partner_discount(self):
        self.order.onchange_partner_id()
        self.assertEqual(
            self.order.general_discount, self.partner.purchase_general_discount
        )

    def test_02_sale_order_values(self):
        self.order.general_discount = 10
        self.order.action_update_general_discount()
        self.assertEqual(self.order.order_line.price_subtotal, 900.00)

    def _get_ctx_from_view(self, res):
        order_xml = etree.XML(res["arch"])
        order_line_path = "//field[@name='order_line']"
        order_line_field = order_xml.xpath(order_line_path)[0]
        return order_line_field.attrib.get("context", "{}")

    def test_03_default_line_discount_value(self):
        res = self.order.fields_view_get(
            view_id=self.env.ref(
                "purchase_order_general_discount.purchase_order_form"
            ).id,
            view_type="form",
        )
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_discount" in ctx)
        view = self.View.create(
            {
                "name": "test",
                "type": "form",
                "model": "purchase.order",
                "arch": """
                <data>
                    <field name='order_line'
                        context="{'default_product_uom_qty': 3.0}">
                    </field>
                </data>
            """,
            }
        )
        res = self.order.fields_view_get(view_id=view.id, view_type="form")
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_discount" in ctx)

    def test_04_no_seller_purchase_supplier_discount_real_disabled(self):
        """
        Tests that if the quantity of a product is below the supplier's minimum quantity,
        the checkbow 'Real Purchase Supplier Discount' is disabled,
        the discounts are kept in the purchase line.
        """
        self.env["product.supplierinfo"].create(
            {
                "min_qty": 10.0,
                "name": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "discount": 20.0,
            }
        )
        purchase_order = common.Form(self.env["purchase.order"])
        purchase_order.partner_id = self.partner
        purchase_order = purchase_order.save()
        purchase_order.company_id.purchase_supplier_discount_real = False
        with common.Form(purchase_order) as po:
            with po.order_line.new() as line:
                line.product_id = self.product
                line.product_qty = 1
        self.assertEqual(purchase_order.order_line[0].discount, 20.0)

    def test_05_no_seller_purchase_supplier_discount_real_enabled(self):
        """
        Tests that if the quantity of a product is below the supplier's minimum quantity,
        the checkbow 'Real Purchase Supplier Discount' is enabled,
        the discounts is set to purchase_general_discount in the purchase line.
        """
        self.env["product.supplierinfo"].create(
            {
                "min_qty": 10.0,
                "name": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "discount": 20.0,
            }
        )
        purchase_order = common.Form(self.env["purchase.order"])
        purchase_order.partner_id = self.partner
        purchase_order = purchase_order.save()
        purchase_order.company_id.purchase_supplier_discount_real = True
        with common.Form(purchase_order) as po:
            with po.order_line.new() as line:
                line.product_id = self.product
                line.product_qty = 1
        self.assertEqual(
            purchase_order.order_line[0].discount,
            self.partner.purchase_general_discount,
        )
