# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseInvoiceStatusLine(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_12")
        self.product_order = self.env.ref("product.product_product_4")
        self.product_received = self.env.ref("product.product_product_6")
        self.product_order.write({"purchase_method": "purchase"})
        self.product_received.write({"purchase_method": "receive"})

    def _create_purchase_order(self, product, qty):
        """Helper to create and confirm a PO for a given product and qty."""
        po_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_qty": qty,
                        "price_unit": 10.0,
                    },
                )
            ],
        }
        po = self.env["purchase.order"].create(po_vals)
        po.button_confirm()
        return po

    def test_force_invoice_logic(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_order.id,
                            "product_qty": 10,
                            "price_unit": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_order.id,
                            "product_qty": 5,
                            "price_unit": 20.0,
                        },
                    ),
                ],
            }
        )
        po.button_confirm()
        line1 = po.order_line[0]
        line2 = po.order_line[1]
        self.assertEqual(line1.invoice_status, "to invoice")
        self.assertEqual(line2.invoice_status, "to invoice")
        self.assertFalse(po.force_invoiced, "PO should not be forced initially")
        line1.force_invoiced = True
        self.assertEqual(
            line1.invoice_status, "invoiced", "L1 status should be invoiced"
        )
        self.assertFalse(po.force_invoiced, "PO not forced if only one line is done")
        line2.force_invoiced = True
        self.assertEqual(
            line2.invoice_status, "invoiced", "L2 status should be invoiced"
        )
        self.assertTrue(
            po.force_invoiced, "PO should be forced when all lines are invoiced"
        )
        line1.force_invoiced = False
        self.assertEqual(line1.invoice_status, "to invoice", "L1 status should revert")
        self.assertFalse(
            po.force_invoiced, "PO should be un-forced if one line reverts"
        )
        po.force_invoiced = True
        self.assertTrue(line1.force_invoiced, "L1 should be forced by PO")
        self.assertTrue(line2.force_invoiced, "L2 should be forced by PO")
        self.assertEqual(line1.invoice_status, "invoiced")
        self.assertEqual(line2.invoice_status, "invoiced")
        po.force_invoiced = False
        self.assertFalse(line1.force_invoiced, "L1 should be un-forced by PO")
        self.assertFalse(line2.force_invoiced, "L2 should be un-forced by PO")
        self.assertEqual(line1.invoice_status, "to invoice")
        self.assertEqual(line2.invoice_status, "to invoice")
