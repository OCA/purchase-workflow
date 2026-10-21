# Copyright 2026 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseFixedDiscount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "service"}
        )
        cls.purchase = cls.env["purchase.order"].create(
            {"name": "Test PO", "partner_id": cls.partner.id}
        )
        cls.po_line = cls.env["purchase.order.line"]
        cls.purchase_line1 = cls.po_line.create(
            {
                "order_id": cls.purchase.id,
                "name": "Line 1",
                "price_unit": 200.0,
                "product_qty": 1,
                "product_id": cls.product.id,
                "taxes_id": [Command.set([cls.tax.id])],
            }
        )

    def test_01_discounts(self):
        """Tests multiple discounts in line with taxes."""
        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.edit(0) as line:
                line.discount_fixed = 20.0
                self.assertEqual(line.discount, 10.0)
                self.assertEqual(line.price_subtotal, 180.0)

        self.assertEqual(self.purchase.amount_total, 207.00)

        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.edit(0) as line:
                line.product_qty = 2
                line.price_unit = 200.0
                self.assertEqual(line.discount, 10.0)
                self.assertEqual(line.price_subtotal, 360.0)

        self.assertEqual(self.purchase.amount_total, 414.00)

        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.edit(0) as line:
                line.product_qty = 1
                line.price_unit = 200.0
                line.discount_fixed = 0.0
                line.discount = 50.0
                self.assertEqual(line.price_subtotal, 100.0)

        self.assertEqual(self.purchase.amount_total, 115.00)

        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.new() as line2:
                line2.product_id = self.product2
                line2.product_qty = 1
                line2.price_unit = 100.0
                line2.discount_fixed = 5.0
                self.assertEqual(line2.discount, 5.0)
                self.assertEqual(line2.price_subtotal, 95.0)

        #
        self.assertEqual(self.purchase.amount_total, 224.25)

    def test_02_fixed_discount_mismatch(self):
        """Tests fixed discount mismatch."""
        with self.assertRaisesRegex(
            ValidationError,
            "Please correct one of the discounts",
        ):
            with Form(self.purchase) as purchase_order:
                with purchase_order.order_line.edit(0) as line:
                    line.discount_fixed = 20.0
                    line.discount = 5.0

    def test_03_fixed_discount_invoice(self):
        """Test discount_fixed value propagation to account.move.
        Case of editing order line by using UI.
        """
        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.edit(0) as line:
                line.discount_fixed = 20.0

        self.purchase.button_confirm()
        self.purchase.action_create_invoice()

        self.assertEqual(
            self.purchase.invoice_ids.invoice_line_ids.discount_fixed, 20.0
        )
        self.assertEqual(self.purchase.invoice_ids.invoice_line_ids.discount, 10.0)

        self.assertEqual(self.purchase.invoice_ids.tax_totals["base_amount"], 180.0)
        self.assertEqual(self.purchase.invoice_ids.tax_totals["total_amount"], 207.0)

    def test_04_fixed_discount_without_price(self):
        with Form(self.purchase) as purchase_order:
            with purchase_order.order_line.edit(0) as line:
                line.product_qty = 1.0
                line.price_unit = 0.0
                line.discount_fixed = 50.0
                self.assertEqual(line.discount, 0.0)
                self.assertEqual(line.price_subtotal, 0.0)
        self.assertEqual(self.purchase.amount_total, 0.0)

    def test_05_fixed_discount_invoice(self):
        """Test discount_fixed value propagation to account.move.
        Case of editing order line without using UI (onchange would be not triggered).
        """
        self.purchase.order_line.discount_fixed = 20.0

        self.purchase.button_confirm()
        self.purchase.action_create_invoice()

        invoices = self.purchase.invoice_ids
        invoices.invoice_line_ids._onchange_discount_fixed()
        self.assertEqual(invoices.invoice_line_ids.discount_fixed, 20.0)
        self.assertEqual(invoices.invoice_line_ids.discount, 10.0)

        self.assertEqual(invoices.tax_totals["base_amount"], 180.0)
        self.assertEqual(invoices.tax_totals["total_amount"], 207.0)
