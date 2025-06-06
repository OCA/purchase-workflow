# Copyright 2019 Tecnativa - David Vidal
# Copyright 2022 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


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
        order_form = Form(cls.env["purchase.order"])
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

    def test_03_get_view_set_default_line_discount_value(self):
        company = self.order.company_id
        company.purchase_general_discount_field = "discount"
        po_form_view_xmlid = "purchase_order_general_discount.purchase_order_form"
        with Form(self.order, po_form_view_xmlid) as order_form:
            order_form.general_discount = 8
            with order_form.order_line.edit(0) as line_form:
                self.assertEqual(line_form.discount, 8)
            order_form.general_discount = 10
            with order_form.order_line.edit(0) as line_form:
                self.assertEqual(line_form.discount, 10)
