# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields
from odoo.tests import Form, common, tagged


@tagged("-at_install", "post_install")
class TestPurchaseOrderAutoLock(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # ENVIRONMENTS
        self.purchase_order = self.env["purchase.order"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.account_model = self.env["account.account"]
        self.am_model = self.env["account.move"]

        self.product_id_1.write({"purchase_method": "purchase"})
        self.po_vals = {
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
                        "date_planned": fields.Datetime.now(),
                    },
                ),
            ],
        }
        self.po = self.purchase_order.create(self.po_vals)
        self.currency_eur = self.env.ref("base.EUR")
        self.supplier = self.env["res.partner"].create({"name": "Test supplier"})

    def test_00_purchase_order_not_received(self):
        """
        The PO is not even received
        """
        self.assertEqual(self.po.invoice_status_validated, "no")
        self.po.button_confirm()
        self.assertEqual(self.po.invoice_status_validated, "to invoice")

    def test_01_purchase_order_received_not_invoiced(self):
        """Test is marked as fully received and to invoice"""
        self.po.button_confirm()
        self.po.picking_ids[0].button_validate()
        self.assertEqual(self.po.invoice_status_validated, "to invoice")

    def test_02_purchase_order_received_invoiced_not_posted(self):
        """If the invoice is not posted is the same thing"""
        self.po.button_confirm()
        self.po.picking_ids.move_line_ids.write({"qty_done": 5})
        self.po.picking_ids[0].button_validate()
        move_form = Form(self.am_model.with_context(default_move_type="in_invoice"))
        move_form.partner_id = self.po.partner_id
        move_form.invoice_date = fields.Date().today()
        move_form.purchase_vendor_bill_id = self.env["purchase.bill.union"].browse(
            -self.po.id
        )
        move_form.save()
        self.assertEqual(self.po.invoice_status_validated, "to invoice")

    def test_03_purchase_order_received_invoiced_posted(self):
        """
        The invoiced and validated
        """
        self.po.button_confirm()
        self.po.picking_ids[0].button_validate()
        move_form = Form(self.am_model.with_context(default_move_type="in_invoice"))
        move_form.partner_id = self.po.partner_id
        move_form.invoice_date = fields.Date().today()
        move_form.purchase_vendor_bill_id = self.env["purchase.bill.union"].browse(
            -self.po.id
        )
        invoice = move_form.save()
        move_form.partner_id = self.supplier
        move_form.currency_id = self.currency_eur
        move_form.invoice_date = datetime.now()
        invoice = move_form.save()
        invoice.action_post()
        # Run the action and check it is closed
        self.assertEqual(self.po.invoice_status_validated, "invoiced")
