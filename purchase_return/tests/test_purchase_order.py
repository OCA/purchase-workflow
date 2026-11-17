from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPurchaseOrder(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.service_order = cls.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "purchase_method": "purchase",
                "default_code": "PRE-PAID",
                "taxes_id": False,
            }
        )

    def test_01(self):
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (0, 0, {"product_id": self.service_order.id, "product_qty": 1.0}),
                ],
            }
        )
        self.assertEqual(purchase_order.invoice_status, "no")
        purchase_order.button_confirm()

        self.assertEqual(purchase_order.invoice_status, "to invoice")
        for line in purchase_order.order_line:
            self.assertEqual(line.product_qty, 1.0)
            self.assertEqual(line.qty_invoiced, 0.0)
        purchase_order.action_create_invoice()
        self.assertEqual(purchase_order.invoice_status, "invoiced")
        invoice = purchase_order.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 1.0)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        wizard_refund = (
            self.env["account.move.reversal"]
            .with_context(
                active_ids=invoice.ids,
                active_model="account.move",
            )
            .create(
                {
                    "refund_method": "refund",
                    "reason": "Refun reason",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        res_reverse = wizard_refund.reverse_moves()
        invoice_refund = self.env["account.move"].browse(res_reverse["res_id"])
        self.assertTrue(invoice_refund)
