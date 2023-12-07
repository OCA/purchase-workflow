# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestPurchaseManualAddSupplierinfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        partner = cls.env.ref("base.res_partner_1")
        product_6 = cls.env.ref("product.product_product_6")
        product_7 = cls.env.ref("product.product_product_7")
        products = product_6 + product_7
        products.write({"seller_ids": [(6, 0, [])]})
        po = Form(cls.env["purchase.order"])
        po.partner_id = partner
        for product in products:
            with po.order_line.new() as po_line:
                po_line.product_id = product
        cls.purchase = po.save()
        cls.purchase.button_confirm()

    def test_update_supplierinfo_from_purchase(self):
        self.assertFalse(self.purchase.all_supplierinfo_ok)
        action_window = self.purchase.update_supplierinfo()
        while self.purchase.order_line.filtered(lambda s: not s.supplierinfo_ok):
            supplier_form = Form(
                self.env["product.supplierinfo"].with_context(action_window["context"])
            )
            supplier = supplier_form.save()
            action_window = supplier.update_from_purchase()
        self.assertTrue(self.purchase.all_supplierinfo_ok)

    def test_update_supplierinfo_from_purchase_line(self):
        self.assertFalse(self.purchase.order_line[0].supplierinfo_ok)
        action_window = self.purchase.order_line[0].action_create_missing_supplierinfo()
        supplier_form = Form(
            self.env["product.supplierinfo"].with_context(action_window["context"])
        )
        supplier_form.save()
        self.assertTrue(self.purchase.order_line[0].supplierinfo_ok)
