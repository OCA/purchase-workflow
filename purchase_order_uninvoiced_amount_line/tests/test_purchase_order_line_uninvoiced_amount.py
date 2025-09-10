# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderLineUninvoicedAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.account_move_model = cls.env["account.move"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.res_partner_model.create(
            {"name": "Partner 1", "supplier_rank": 1, "is_company": True}
        )
        cls.product_categ = cls.product_category_model.create({"name": "Test category"})
        cls.uom_categ = cls.env["uom.category"].create({"name": "Category 1"})
        cls.uom1 = cls.env["uom.uom"].create(
            {
                "name": "UOM 1",
                "category_id": cls.uom_categ.id,
                "factor": 1,
                "active": True,
                "uom_type": "reference",
            }
        )
        # Products
        cls.product_category = cls.env["product.category"].create(
            {"name": "Test Product category"}
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "sale_ok": True,
                "type": "consu",
                "categ_id": cls.product_category.id,
                "description_sale": "Test Description Sale",
                "purchase_method": "receive",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "sale_ok": True,
                "type": "consu",
                "categ_id": cls.product_category.id,
                "description_sale": "Test Description Sale 2",
                "purchase_method": "purchase",
            }
        )

    def _create_purchase_with_lines(self, lines_data):
        purchase = self.purchase_order_model.create(
            {"company_id": self.company.id, "partner_id": self.partner.id}
        )
        lines = []
        for line_data in lines_data:
            line = self.purchase_order_line_model.create(
                {
                    "name": line_data["product"].name,
                    "product_id": line_data["product"].id,
                    "product_qty": line_data["qty"],
                    "product_uom": line_data["product"].uom_po_id.id,
                    "price_unit": line_data["price"],
                    "date_planned": fields.Date.today(),
                    "order_id": purchase.id,
                }
            )
            lines.append(line)

        purchase.button_confirm()
        for i, line in enumerate(lines):
            line.qty_received = lines_data[i]["received"]
        return purchase, lines

    def _create_invoice_from_purchase(self, purchase):
        res = purchase.action_create_invoice()
        return self.env["account.move"].browse(res["res_id"])

    def test_single_line_not_invoiced(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 5, "received": 5, "price": 100.0}]
        )
        line = lines[0]
        self.assertEqual(line.amount_uninvoiced, 500.0)
        self.assertEqual(line.invoice_status, "to invoice")

    def test_single_line_no_receive(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 5, "received": 0, "price": 100.0}]
        )
        line = lines[0]
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_single_line_partial_invoice(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 10, "received": 10, "price": 50.0}]
        )
        line = lines[0]
        self.assertEqual(line.amount_uninvoiced, 500.0)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 6
        self.assertEqual(line.amount_uninvoiced, 200.0)

    def test_single_line_fully_invoiced(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 3, "received": 3, "price": 75.0}]
        )
        line = lines[0]
        self._create_invoice_from_purchase(purchase)
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_multiple_lines_different_amounts(self):
        purchase, lines = self._create_purchase_with_lines(
            [
                {"product": self.product_1, "qty": 5, "received": 5, "price": 100.0},
                {"product": self.product_2, "qty": 3, "received": 2, "price": 200.0},
            ]
        )
        line1, line2 = lines
        # Line 1: receive policy, 5 received - 0 invoiced = 5 * 100 = 500
        self.assertEqual(line1.amount_uninvoiced, 500.0)
        # Line 2: purchase policy, 3 ordered - 0 invoiced = 3 * 200 = 600
        self.assertEqual(line2.amount_uninvoiced, 600.0)

    def test_on_ordered_quantities_policy(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_2, "qty": 10, "received": 0, "price": 60.0}]
        )
        line = lines[0]
        self.assertEqual(line.amount_uninvoiced, 600.0)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 4
        self.assertEqual(line.amount_uninvoiced, 360.0)

    def test_zero_quantity_line(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 0, "received": 0, "price": 100.0}]
        )
        line = lines[0]
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_over_invoicing(self):
        purchase, lines = self._create_purchase_with_lines(
            [{"product": self.product_1, "qty": 5, "received": 5, "price": 80.0}]
        )
        line = lines[0]
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 8
        # Over-invoicing should result in 0, not negative
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_mixed_policies_multiple_lines(self):
        self.product_1.purchase_method = "receive"
        self.product_2.purchase_method = "purchase"
        purchase, lines = self._create_purchase_with_lines(
            [
                {"product": self.product_1, "qty": 10, "received": 8, "price": 25.0},
                {"product": self.product_2, "qty": 6, "received": 3, "price": 150.0},
            ]
        )

        line1, line2 = lines
        self.assertEqual(line1.amount_uninvoiced, 200.0)
        self.assertEqual(line2.amount_uninvoiced, 900.0)
        invoice = self._create_invoice_from_purchase(purchase)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 5
            with invoice_form.invoice_line_ids.edit(1) as line_form:
                line_form.quantity = 2
        self.assertEqual(line1.amount_uninvoiced, 75.0)
        self.assertEqual(line2.amount_uninvoiced, 600.0)
