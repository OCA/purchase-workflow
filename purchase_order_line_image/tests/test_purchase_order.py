from odoo.tests.common import TransactionCase


class TestPurchaseOrderLineInvoiceWizard(TransactionCase):
    def setUp(self):
        super().setUp()

        self.purchase_order = self.env["purchase.order"]

    def test_enabled_show_product_image_in_purchase_report(self):
        """
        'Show Product Image In Purchase Report' mode is enabled in settings.
        Test whether the option is enabled or disabled
        """
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_order_line_image.show_product_image_in_purchase_report", True
        )
        self.assertEqual(
            self.purchase_order.check_show_product_image_in_purchase_report(),
            "True",
            "Must be equal to True",
        )

    def test_disabled_show_product_image_in_purchase_report(self):
        """
        'Show Product Image In Purchase Report' mode is disabled in settings.
        Test whether the option is enabled or disabled
        """
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_order_line_image.show_product_image_in_purchase_report", False
        )

        self.assertEqual(
            self.purchase_order.check_show_product_image_in_purchase_report(),
            False,
            "Must be equal to False",
        )
