# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
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

    def _assert_visible_sequence(self, lines):
        self.assertEqual(
            lines.mapped("visible_sequence"), list(range(1, len(lines) + 1))
        )

    def test_sequence_does_not_trigger_line_onchange(self):
        """Reordering lines must not send one onchange per line."""
        lines = self.PurchaseOrderLine
        self.assertFalse(
            lines._has_onchange(
                lines._fields["sequence"], [lines._fields["visible_sequence"]]
            )
        )

    def test_reorder_lines(self):
        po = self._create_purchase_order()
        line_1, line_2 = po.order_line
        line_2.sequence = line_1.sequence - 1
        self._assert_visible_sequence(line_2 + line_1)

    def test_reorder_lines_from_order(self):
        """Resequence all lines at once, as the web client does on save."""
        po = self._create_purchase_order()
        section = self.PurchaseOrderLine.create(
            {
                "name": "Section",
                "order_id": po.id,
                "display_type": "line_section",
                "product_qty": 0,
            }
        )
        lines = po.order_line - section
        po.write(
            {
                "order_line": [
                    Command.update(line.id, {"sequence": seq})
                    for seq, line in enumerate(reversed(lines + section))
                ]
            }
        )
        self._assert_visible_sequence(lines.sorted("sequence"))
        self.assertFalse(section.visible_sequence)

    def test_add_line(self):
        po = self._create_purchase_order()
        line_1, line_2 = po.order_line
        new_line = line_1.copy({"sequence": line_1.sequence - 1})
        self._assert_visible_sequence(new_line + line_1 + line_2)
