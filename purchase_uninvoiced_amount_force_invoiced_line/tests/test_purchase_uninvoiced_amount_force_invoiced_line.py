# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestPurchaseUninvoicedAmountForceInvoicedLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.product_1 = self.env.ref("product.product_product_8")
        self.product_2 = self.env.ref("product.product_product_11")
        self.product_1.purchase_method = "receive"
        self.product_2.purchase_method = "purchase"

    def _create_purchase_order(self, lines_data):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner
        for line_data in lines_data:
            with purchase_form.order_line.new() as line_form:
                line_form.product_id = line_data["product"]
                line_form.product_qty = line_data["qty"]
                line_form.price_unit = line_data["price"]
        purchase = purchase_form.save()
        purchase.button_confirm()
        for i, line_data in enumerate(lines_data):
            if "received" in line_data:
                purchase.order_line[i].qty_received = line_data["received"]
        return purchase

    def test_force_invoiced_false_normal_calculation(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_1, "qty": 10, "received": 8, "price": 50.0}]
        )
        line = purchase.order_line[0]
        line.force_invoiced = False
        self.assertEqual(line.amount_uninvoiced, 500.0)

    def test_force_invoiced_true_zero_amount(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_1, "qty": 10, "received": 8, "price": 50.0}]
        )
        line = purchase.order_line[0]
        line.force_invoiced = True
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_force_invoiced_with_partial_invoice(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_1, "qty": 10, "received": 10, "price": 100.0}]
        )
        line = purchase.order_line[0]
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "purchase_id": purchase.id,
                "invoice_date": "2025-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "quantity": 5,
                            "price_unit": 100.0,
                            "purchase_line_id": line.id,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        line.force_invoiced = False
        self.assertEqual(line.amount_uninvoiced, 500.0)
        line.force_invoiced = True
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_multiple_lines_mixed_force_invoiced(self):
        purchase = self._create_purchase_order(
            [
                {"product": self.product_1, "qty": 5, "price": 80.0},
                {"product": self.product_2, "qty": 3, "price": 120.0},
            ]
        )
        line1, line2 = purchase.order_line
        line1.force_invoiced = False
        line2.force_invoiced = True
        self.assertEqual(line1.amount_uninvoiced, 400.0)
        self.assertEqual(line2.amount_uninvoiced, 0.0)

    def test_purchase_policy_with_force_invoiced(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_2, "qty": 8, "price": 75.0}]
        )
        line = purchase.order_line[0]
        line.force_invoiced = False
        self.assertEqual(line.amount_uninvoiced, 600.0)
        line.force_invoiced = True
        self.assertEqual(line.amount_uninvoiced, 0.0)

    def test_force_invoiced_toggle(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_1, "qty": 6, "price": 90.0}]
        )
        line = purchase.order_line[0]
        line.force_invoiced = False
        self.assertEqual(line.amount_uninvoiced, 540.0)
        line.force_invoiced = True
        self.assertEqual(line.amount_uninvoiced, 0.0)
        line.force_invoiced = False
        self.assertEqual(line.amount_uninvoiced, 540.0)

    def test_receive_policy_ignores_qty_received_until_invoiced(self):
        purchase = self._create_purchase_order(
            [{"product": self.product_1, "qty": 10, "received": 0, "price": 50.0}]
        )
        line = purchase.order_line[0]
        self.assertEqual(line.amount_uninvoiced, 500.0)
        line.qty_received = 8
        self.assertEqual(line.amount_uninvoiced, 500.0)
        inv_partial = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "purchase_id": purchase.id,
                "invoice_date": "2025-01-02",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "quantity": 3,
                            "price_unit": 50.0,
                            "purchase_line_id": line.id,
                        },
                    )
                ],
            }
        )
        inv_partial.action_post()
        self.assertEqual(line.amount_uninvoiced, 350.0)
        line.qty_received = 10
        self.assertEqual(line.amount_uninvoiced, 350.0)
        inv_rest = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "purchase_id": purchase.id,
                "invoice_date": "2025-01-03",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "quantity": 7,
                            "price_unit": 50.0,
                            "purchase_line_id": line.id,
                        },
                    )
                ],
            }
        )
        inv_rest.action_post()
        self.assertEqual(line.amount_uninvoiced, 0.0)
