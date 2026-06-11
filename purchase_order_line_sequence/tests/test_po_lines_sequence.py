# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged

from .common import PurchaseOrderLineSequenceCase


@tagged("post_install", "-at_install")
class TestPurchaseOrder(PurchaseOrderLineSequenceCase):
    def test_purchase_order_line_visible_sequence(self):
        po = self._create_purchase_order()
        self.assertEqual(po.order_line[0].visible_sequence, 1)
        self.assertEqual(po.order_line[1].visible_sequence, 2)
        po2 = po.copy()
        self.assertEqual(
            po.order_line[0].visible_sequence,
            po2.order_line[0].visible_sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            po.order_line[1].visible_sequence,
            po2.order_line[1].visible_sequence,
            "The Sequence is not copied properly",
        )
        po_form = Form(po2)
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = self.product_id_1
            self.assertEqual(po_line_form.sequence, po2.max_line_sequence)

    def test_invoice_sequence(self):
        """
        Verify that the sequence is correctly assigned to the account move associated
        with the purchase order line it references.
        """
        po = self._create_purchase_order()
        po.button_confirm()
        po.order_line.qty_received = 5
        result = po.action_create_invoice()
        invoice = self.AccountInvoice.browse(result["res_id"])
        self.assertEqual(
            str(po.order_line[0].visible_sequence),
            invoice.line_ids[0].related_po_sequence,
        )
        self.assertEqual(
            str(po.order_line[1].visible_sequence),
            invoice.line_ids[1].related_po_sequence,
        )

    def test_invoice_multiple_orders_sequence(self):
        """
        Verify that the sequence is correctly assigned to the account move associated
        with the purchase order line it references,
        when adding different POs to the same invoice.
        Format expected:
        - PO12345/1  -  PO Name + "/" + Sequence
        """
        po = self._create_purchase_order()
        po.button_confirm()
        po.order_line.qty_received = 5
        po2 = self._create_purchase_order()
        po2.button_confirm()
        po2.order_line.qty_received = 2

        orders = self.PurchaseOrder.search([("id", "in", [po.id, po2.id])])
        result = orders.action_create_invoice()
        invoice = self.AccountInvoice.search([("id", "=", result["res_id"])], limit=1)

        self.assertTrue(invoice)
        self.assertTrue(len(invoice.invoice_origin.split(",")), 2)

        self.assertEqual(
            invoice.invoice_line_ids[0].related_po_sequence,
            f"{po2.name}/{po2.order_line[0].visible_sequence}",
        )
        self.assertEqual(
            invoice.invoice_line_ids[3].related_po_sequence,
            f"{po.name}/{po.order_line[1].visible_sequence}",
        )
