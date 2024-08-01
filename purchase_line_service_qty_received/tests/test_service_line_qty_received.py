# Copyright 2024 Raumschmiede GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.tests import Form, tagged

from .common import TestServiceQtyReceivedCommon


@tagged("post_install", "-at_install")
class TestServiceQtyReceived(TestServiceQtyReceivedCommon):
    def test_01_reception_qty_received(self):
        self._new_purchase_order()
        self._check_qty_received(0)

        self.po.button_confirm()
        # Confirm creates picking, no qty_received is set yet, service line
        # must not be received
        self._check_qty_received(0)

        # Receiving the PO updates the qty_received of stock PO lines, thus
        # qty_received of the service lines must be set
        self._receive_order()
        self._check_qty_received(2)

        # Returning everything back to the supplier sets qty_received for the returned
        # stock lines to 0, the same must happen with the service lines
        self._return_order()
        self._check_qty_received(0)

    def test_02_reception_qty_received_purchase_method(self):
        # If the product has the other purchase method, the current implementation
        # must not work with this configuration
        self.reception.purchase_method = "purchase"
        self._new_purchase_order()
        self._check_qty_received(0)

        self.po.button_confirm()
        self._check_qty_received(0)

    def test_03_invoice_status(self):
        self._new_purchase_order()
        self.po.button_confirm()
        self._receive_order()
        self.assertEqual(self.po.invoice_status, "to invoice")

        # Test usual behaviour. Picking has been received. The created invoice
        # must contain the service product and PO invoice status must be correct
        invoice = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        self.assertIn(self.reception, invoice.invoice_line_ids.product_id)
        self.assertEqual(self.po.invoice_status, "invoiced")

        # Returning the PO must "revert" the invoice, PO must be invoiceable again
        self._return_order()
        self.assertEqual(self.po.invoice_status, "to invoice")

        # Creating a credit note must work to get the money back from the supplier
        invoice = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        self.assertEqual(self.po.invoice_status, "invoiced")
        self.assertIn(self.reception, invoice.invoice_line_ids.product_id)

        invoice_form = Form(invoice)
        invoice_form.invoice_line_ids.remove(index=1)
        invoice = invoice_form.save()
        # Removing the service product from the invoice must affect the PO's invoice
        # status as the PO is now not fully invoiced anymore
        self.assertEqual(self.po.invoice_status, "to invoice")
