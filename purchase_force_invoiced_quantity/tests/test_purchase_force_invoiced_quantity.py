# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestPurchaseForceInvoicedQTY(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.purchase_order_obj = cls.env["purchase.order"]
        cls.purchase_order_line_obj = cls.env["purchase.order.line"]

        cls.customer = cls.partner_a
        cls.product_1 = cls.product_a
        cls.product_2 = cls.product_b
        (cls.product_1 | cls.product_2).write({"purchase_method": "receive"})

    def test_purchase_order(self):
        po = self.purchase_order_obj.create({"partner_id": self.customer.id})
        pol1 = self.purchase_order_line_obj.create(
            {"product_id": self.product_1.id, "product_qty": 3, "order_id": po.id}
        )
        pol2 = self.purchase_order_line_obj.create(
            {"product_id": self.product_2.id, "product_qty": 2, "order_id": po.id}
        )

        # confirm quotation
        po.button_confirm()
        # update quantities delivered
        pol1.qty_received = 1
        pol2.qty_received = 2

        pol2.force_invoiced_qty = 3
        self.assertEqual(
            pol2.qty_to_invoice, -1, msg="The quantity to invoice should be -1"
        )
        self.assertEqual(
            po.invoice_status, "to invoice", "The invoice status should be To Invoice"
        )

        po.action_create_invoice()
        self.assertEqual(
            po.invoice_status, "invoiced", "The invoice status should be Invoiced"
        )
