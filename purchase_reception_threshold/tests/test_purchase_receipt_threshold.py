# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import RecordCapturer, TransactionCase


class TestPurchaseReceptionThreshold(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.receipt_threshold = 0.2  # 20%

        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Supplier", "use_threshold": True}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "purchase_ok": True,
            }
        )

        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10.0,
                            "price_unit": 5.0,
                            "product_uom": cls.product.uom_po_id.id,
                            "date_planned": "2026-03-20",
                        },
                    )
                ],
            }
        )
        cls.order.button_confirm()

    def test_01_action_done_backorder_within_threshold(self):
        """Validating a picking within threshold creates no backorder."""
        picking = self.order.picking_ids[0]
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = 9  # within 20% of 10 → range [8, 12]
            move.picked = True
        with RecordCapturer(
            self.env["stock.picking"], [("backorder_id", "=", picking.id)]
        ) as rc:
            picking._action_done()
        self.assertFalse(rc.records)

    def test_02_action_done_backorder_outside_threshold(self):
        """Validating a picking outside threshold creates a backorder."""
        picking = self.order.picking_ids[0]
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = 5  # outside threshold
            move.picked = True
        with RecordCapturer(
            self.env["stock.picking"], [("backorder_id", "=", picking.id)]
        ) as rc:
            picking._action_done()
        self.assertTrue(rc.records)
