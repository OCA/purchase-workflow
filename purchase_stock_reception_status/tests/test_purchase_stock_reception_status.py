# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseStockReceptionStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "is_company": True,
                "supplier_rank": 1,
            }
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
                "purchase_method": "receive",
                "list_price": 100.0,
            }
        )

    def test_01_receipt_status_functionality(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": po.id,
                "product_id": self.product_1.id,
                "name": self.product_1.name,
                "product_qty": 10.0,
                "product_uom": self.product_1.uom_po_id.id,
                "price_unit": 100.0,
                "date_planned": fields.Date.today(),
            }
        )
        po.button_confirm()
        self.assertEqual(po.receipt_status, "pending")
        picking = po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids[0].quantity = 5.0
        picking.move_ids.picked = True
        backorder_wizard_dict = picking.button_validate()
        if backorder_wizard_dict:
            backorder_wizard = Form(
                self.env[backorder_wizard_dict["res_model"]].with_context(
                    **backorder_wizard_dict["context"]
                )
            ).save()
            backorder_wizard.process()
        self.assertEqual(po.receipt_status, "partial")
        po.button_done()
        po.force_received = True
        self.assertEqual(po.receipt_status, "full")

    def test_02_receipt_status_draft_state(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": po.id,
                "product_id": self.product_1.id,
                "name": self.product_1.name,
                "product_qty": 10.0,
                "product_uom": self.product_1.uom_po_id.id,
                "price_unit": 100.0,
                "date_planned": fields.Date.today(),
            }
        )
        self.assertEqual(po.receipt_status, "pending")

    def test_03_receipt_status_over_received(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": po.id,
                "product_id": self.product_1.id,
                "name": self.product_1.name,
                "product_qty": 10.0,
                "product_uom": self.product_1.uom_po_id.id,
                "price_unit": 100.0,
                "date_planned": fields.Date.today(),
            }
        )
        po.button_confirm()
        picking = po.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids[0].quantity = 15.0
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(po.receipt_status, "full")
