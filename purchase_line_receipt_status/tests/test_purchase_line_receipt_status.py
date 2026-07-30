# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.purchase_stock.tests.common import PurchaseTestCommon


class TestPurchaseLineReceiptStatus(PurchaseTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner_a = cls.env["res.partner"].create({"name": "Partner A"})
        cls.product_goods = cls.env["product.product"].create(
            {"name": "Large Desk", "purchase_method": "purchase"}
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Consulting Service",
                "type": "service",
                "purchase_method": "purchase",
            }
        )

        cls.po_vals = {
            "partner_id": cls.partner_a.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_goods.name,
                        "product_id": cls.product_goods.id,
                        "product_qty": 5.0,
                        "product_uom": cls.product_goods.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product_service.name,
                        "product_id": cls.product_service.id,
                        "product_qty": 5.0,
                        "product_uom": cls.product_service.uom_po_id.id,
                        "price_unit": 250.0,
                    },
                ),
            ],
        }
        cls.po = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_line_goods = cls.po.order_line.filtered(
            lambda line: line.product_id == cls.product_goods
        )
        cls.po_line_service = cls.po.order_line.filtered(
            lambda line: line.product_id == cls.product_service
        )

    def test_no_receipt_status_initially(self):
        self.assertEqual(self.po.state, "draft")
        self.assertFalse(self.po_line_goods.line_receipt_status)
        self.assertFalse(self.po_line_service.line_receipt_status)

    def test_receipt_status_after_confirmation(self):
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")
        self.assertEqual(self.po_line_goods.line_receipt_status, "pending")
        # Service lines with type 'service' do not create stock moves
        self.assertEqual(self.po_line_service.line_receipt_status, False)

        # Simulate partial receipt of goods
        picking = self.po.picking_ids
        picking.action_assign()
        move_line = picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_goods
        )
        move_line.qty_done = 3.0
        wiz_act = picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()

        self.assertEqual(self.po_line_goods.line_receipt_status, "partial")
        self.assertEqual(self.po_line_service.line_receipt_status, False)

        backorder_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        backorder_picking.action_assign()
        backorder_move_line = backorder_picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_goods
        )
        backorder_move_line.qty_done = 2.0
        backorder_picking.button_validate()
        self.assertEqual(self.po_line_goods.line_receipt_status, "full")

    def test_cancelled_moves(self):
        self.po.button_confirm()
        picking = self.po.picking_ids
        picking.action_assign()
        move = picking.move_ids.filtered(lambda m: m.product_id == self.product_goods)
        move._action_cancel()
        self.assertFalse(self.po_line_goods.line_receipt_status)

    def test_cancelled_remaining_moves(self):
        self.po.button_confirm()
        picking = self.po.picking_ids
        picking.action_assign()
        # Simulate partial receipt
        move_line = picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_goods
        )
        move_line.qty_done = 3.0
        wiz_act = picking.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()
        self.assertEqual(self.po_line_goods.line_receipt_status, "partial")
        # Cancel remaining move
        backorder_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        backorder_picking.action_cancel()
        self.assertEqual(self.po_line_goods.line_receipt_status, "full")
