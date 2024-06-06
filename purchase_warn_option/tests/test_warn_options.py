# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestWarnOptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.partner_purchase_warn_warning = cls.env["warn.option"].create(
            {
                "name": "warning",
                "allowed_warning_usage": "partner_purchase_warn",
                "allowed_warning_type": "warning",
            }
        )
        cls.partner_purchase_warn_blocking = cls.env["warn.option"].create(
            {
                "name": "block",
                "allowed_warning_usage": "partner_purchase_warn",
                "allowed_warning_type": "block",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
            }
        )
        cls.product_purchase_warn_warning = cls.env["warn.option"].create(
            {
                "name": "warning",
                "allowed_warning_usage": "product_purchase_warn",
                "allowed_warning_type": "warning",
            }
        )
        cls.product_purchase_warn_blocking = cls.env["warn.option"].create(
            {
                "name": "block",
                "allowed_warning_usage": "product_purchase_warn",
                "allowed_warning_type": "block",
            }
        )

    def test_partner_warn_options(self):
        """Test Warn Options on Partner Form"""
        with Form(self.partner) as partner_f:
            partner_f.purchase_warn = "warning"
            partner_f.purchase_warn_option = self.partner_purchase_warn_warning
            self.assertEqual(partner_f.purchase_warn_msg, "warning")
            partner_f.purchase_warn = "block"
            partner_f.purchase_warn_option = self.partner_purchase_warn_blocking
            self.assertEqual(partner_f.purchase_warn_msg, "block")

    def test_product_warn_options(self):
        """Test Warn Options on Product Form"""
        with Form(self.product) as product_f:
            product_f.purchase_line_warn = "warning"
            product_f.purchase_line_warn_option = self.product_purchase_warn_warning
            self.assertEqual(product_f.purchase_line_warn_msg, "warning")
            product_f.purchase_line_warn = "block"
            product_f.purchase_line_warn_option = self.product_purchase_warn_blocking
            self.assertEqual(product_f.purchase_line_warn_msg, "block")
