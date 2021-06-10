# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseOrderLineInvoiceWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")
        po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                )
            ],
        }
        self.po1 = self.env["purchase.order"].create(po_vals)
        po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                )
            ],
        }
        self.po2 = self.env["purchase.order"].create(po_vals)

    def test1(self):
        purchase_order_lines = self.po1.order_line + self.po2.order_line
        wizard = (
            self.env["purchase.order.line.invoice.wizard"]
            .with_context(active_ids=purchase_order_lines.ids)
            .create({})
        )
        line1 = wizard.purchase_order_line_details_ids.filtered(
            lambda x: x.purchase_order_line_id.order_id.id == self.po1.id
        )
        line2 = wizard.purchase_order_line_details_ids.filtered(
            lambda x: x.purchase_order_line_id.order_id.id == self.po2.id
        )

        line1.purchase_order_line_id.qty_to_invoice = 3
        line2.purchase_order_line_id.qty_to_invoice = 4

        res = wizard.create_invoice()
        invoice_id = res["res_id"]
        self.assertTrue(invoice_id)
        invoice = self.env["account.move"].browse(invoice_id)

        self.assertEqual(invoice.partner_id.id, self.partner_id.id)
        self.assertEqual(invoice.move_type, "in_invoice")
        self.assertEqual(
            invoice.invoice_line_ids.filtered(
                lambda x: x.purchase_line_id.id == line1.purchase_order_line_id.id
            ).quantity,
            3,
        )
        self.assertEqual(
            invoice.invoice_line_ids.filtered(
                lambda x: x.purchase_line_id.id == line2.purchase_order_line_id.id
            ).quantity,
            4,
        )
