# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchaseInvoiceStatusLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.partner_a
        cls.product_order = cls.product_a
        cls.product_received = cls.product_b
        cls.product_order.write({"purchase_method": "purchase"})
        cls.product_received.write({"purchase_method": "receive"})

    def test_force_invoice_logic(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_order.id,
                            "product_qty": 10,
                            "price_unit": 10.0,
                        },
                    ),
                    Command.create(
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
            line1.invoice_status, "invoiced", "L1 status should be invoiced when forced"
        )
        self.assertFalse(po.force_invoiced, "PO not forced if only one line is done")
        line2.force_invoiced = True
        self.assertEqual(
            line2.invoice_status, "invoiced", "L2 status should be invoiced when forced"
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
