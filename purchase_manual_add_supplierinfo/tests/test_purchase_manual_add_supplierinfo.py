# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestPurchaseManualAddSupplierinfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_6 = cls.env.ref("product.product_product_6")
        cls.product_7 = cls.env.ref("product.product_product_7")

    def test_update_supplierinfo_from_purchase(self):
        products = self.product_6 + self.product_7
        products.write({"seller_ids": [(6, 0, [])]})
        purchase_order = self._create_purchase_order(self.partner, products)
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.all_supplierinfo_ok, False)
        action_window = purchase_order.update_supplierinfo()
        while purchase_order.order_line.filtered(lambda s: not s.supplierinfo_ok):
            supplier_form = Form(
                self.env["product.supplierinfo"].with_context(action_window["context"])
            )
            supplier = supplier_form.save()
            action_window = supplier.update_from_purchase()
        self.assertEqual(purchase_order.all_supplierinfo_ok, True)

    def test_update_supplierinfo_from_purchase_line(self):
        products = self.product_6
        products.write({"seller_ids": [(6, 0, [])]})
        purchase_order = self._create_purchase_order(self.partner, products)
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.order_line[0].supplierinfo_ok, False)
        action_window = purchase_order.order_line[0].create_missing_supplierinfo()
        supplier_form = Form(
            self.env["product.supplierinfo"].with_context(action_window["context"])
        )
        supplier_form.save()
        self.assertEqual(purchase_order.order_line[0].supplierinfo_ok, True)

    def _create_purchase_order(self, partner, products):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = partner
        for product in products:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
        return order_form.save()
