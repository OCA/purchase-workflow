# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestPurchaseInvoiceMethod(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Supplier",
                "email": "supplier.serv@supercompany.com",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "standard_price": 200.0,
                "list_price": 180.0,
                "type": "service",
                "purchase_method": "receive",
            }
        )

    def test_force_create_invoice_receive(self):

        purchase_order_form = Form(self.env["purchase.order"])
        purchase_order_form.partner_id = self.vendor

        with purchase_order_form.order_line.new() as line:
            line.name = self.product.name
            line.product_id = self.product
            line.product_qty = 4
            line.price_unit = 500

        purchase_order = purchase_order_form.save()
        purchase_order.button_confirm()

        self.assertEqual(purchase_order.invoice_status, "no")
        purchase_order.invoice_method = "purchase"
        self.assertEqual(purchase_order.invoice_status, "to invoice")
        for line in purchase_order.order_line:
            self.assertEqual(line.product_qty, 4)
            self.assertEqual(line.qty_invoiced, 0.0)

        purchase_order.action_create_invoice()
        self.assertEqual(purchase_order.invoice_status, "invoiced")
        for line in purchase_order.order_line:
            self.assertEqual(line.qty_to_invoice, 0.0)
            self.assertEqual(line.qty_invoiced, 4)

    def test_force_create_invoice_purchase(self):
        self.product.purchase_method = "purchase"
        purchase_order_form = Form(self.env["purchase.order"])
        purchase_order_form.partner_id = self.vendor

        with purchase_order_form.order_line.new() as line:
            line.name = self.product.name
            line.product_id = self.product
            line.product_qty = 4
            line.price_unit = 500

        purchase_order = purchase_order_form.save()
        purchase_order.button_confirm()

        self.assertEqual(purchase_order.invoice_status, "to invoice")
        purchase_order.invoice_method = "receive"
        self.assertEqual(purchase_order.invoice_status, "no")

    def test_force_create_invoice_draft(self):
        purchase_order_form = Form(self.env["purchase.order"])
        purchase_order_form.partner_id = self.vendor

        with purchase_order_form.order_line.new() as line:
            line.name = self.product.name
            line.product_id = self.product
            line.product_qty = 4
            line.price_unit = 500

        purchase_order = purchase_order_form.save()
        purchase_order.invoice_method = "purchase"
        self.assertEqual(purchase_order.invoice_status, "no")
        self.assertEqual(purchase_order.order_line.qty_to_invoice, 0)
