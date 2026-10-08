# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestPurchaseManualAddSupplierinfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        partner = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_7")
        products = cls.product_1 + cls.product_2
        products.write({"seller_ids": [(6, 0, [])]})
        po = Form(cls.env["purchase.order"])
        po.partner_id = partner
        for product in products:
            with po.order_line.new() as po_line:
                po_line.product_id = product
        cls.purchase = po.save()
        cls.purchase.button_confirm()
        cls.line_1, cls.line_2 = cls.purchase.order_line

    def _execute_action(self, action):
        return Form(
            self.env["product.supplierinfo"].with_context(action["context"])
        ).save()

    def test_update_supplierinfo_from_purchase(self):
        """Update the first line and skip the second one"""
        self.assertFalse(self.purchase.all_supplierinfo_ok)

        action = self.purchase.update_supplierinfo()
        wizard = self._execute_action(action)
        new_action = wizard.update_from_purchase()
        self.assertEqual(new_action["type"], "ir.actions.act_window")
        self.assertEqual(len(self.product_1.seller_ids), 1)
        self.assertEqual(self.product_1.seller_ids.name, self.purchase.partner_id)

        wizard = self._execute_action(new_action)
        new_action_2 = wizard.update_from_purchase_skip()
        self.assertEqual(
            new_action_2, {}
        )  # nothing to do, all line have been processed
        self.assertFalse(self.product_2.seller_ids)

        self.assertTrue(self.purchase.all_supplierinfo_ok)

    def _get_po_line_wizard(self):
        self.assertFalse(self.line_1.supplierinfo_ok)
        action_window = self.line_1.action_create_missing_supplierinfo()
        supplier_form = Form(
            self.env["product.supplierinfo"].with_context(action_window["context"])
        )
        return supplier_form.save()

    def test_update_supplierinfo_from_purchase_line(self):
        # Launching and saving the wizard should do nothing
        action = self.line_1.action_create_missing_supplierinfo()
        supplier = self._execute_action(action)
        self.assertFalse(self.line_1.supplierinfo_ok)
        self.assertFalse(self.product_1.seller_ids)

        # Updating should generate the missing supplier
        supplier.update_from_purchase()
        self.assertTrue(self.line_1.supplierinfo_ok)
        self.assertEqual(len(self.product_1.seller_ids), 1)

    def test_update_supplierinfo_from_purchase_line_skip(self):
        wizard = self._get_po_line_wizard()
        wizard.update_from_purchase_skip()
        self.assertTrue(self.line_1.supplierinfo_ok)
        self.assertFalse(self.product_1.seller_ids)
