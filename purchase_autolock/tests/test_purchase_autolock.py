from odoo import fields
from odoo.tests.common import Form, SingleTransactionCase


class TestPurchaseAutolock(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_model = cls.env["purchase.order"]
        cls.po = cls.env.ref("purchase.purchase_order_1")

    def _do_picking(self, picking, date):
        """Do picking with only one move on the given date."""
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_lines.filtered(lambda m: m.state != "waiting"):
            move.quantity_done = move.product_qty
        picking.button_validate()

    def test_01_autolock(self):
        """
        Test the PO is locked automatically
        """
        po = self.po.copy()
        po.button_confirm()
        self._do_picking(po.picking_ids, fields.Date.today())
        action = po.action_view_invoice()
        invoice_form = Form(self.env["account.move"].with_context(action["context"]))
        invoice = invoice_form.save()
        invoice.post()
        self.assertNotEqual(po.state, "done")
        po.message_ids._write({"write_date": "1900-01-01"})
        self.po_model.cron_auto_lock_purchase()
        self.assertEqual(po.state, "done")

    def test_02_autolock(self):
        """
        Test the PO is not locked automatically (not fully invoiced)
        """
        po = self.po.copy()
        po.button_confirm()
        self._do_picking(po.picking_ids, fields.Date.today())
        po.message_ids._write({"write_date": "1900-01-01"})
        self.po_model.cron_auto_lock_purchase()
        self.assertNotEqual(po.state, "done")
