# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo.tests.common import TransactionCase, new_test_user, users


class TestProductSupplierinfoSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(cls.env, login="test-internal-user", groups="base.group_user")
        new_test_user(
            cls.env, login="test-purchase-user", groups="purchase.group_purchase_user"
        )

    def _access_supplier_info_from_product_form(self):
        res = self.env["product.template"].get_view(
            view_id=self.ref("product.product_template_form_view"),
            view_type="form",
        )
        return "seller_ids" in res["arch"]

    @users("test-internal-user")
    def test_internal_user_can_access_seller_ids(self):
        self.assertFalse(self._access_supplier_info_from_product_form())

    @users("test-purchase-user")
    def test_purchase_user_user_can_access_seller_ids(self):
        self.assertTrue(self._access_supplier_info_from_product_form())
