# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests import tagged

from odoo.addons.purchase_order_line_sequence.tests.common import (
    PurchaseOrderLineSequenceCase,
)


@tagged("post_install", "-at_install")
class TestPurchaseStockLineSequence(PurchaseOrderLineSequenceCase):
    def test_purchase_order_line_sequence_propagates_to_moves(self):
        po = self._create_purchase_order()
        po.button_confirm()
        move1 = self.env["stock.move"].search(
            [("purchase_line_id", "=", po.order_line[0].id)]
        )
        move2 = self.env["stock.move"].search(
            [("purchase_line_id", "=", po.order_line[1].id)]
        )
        self.assertEqual(
            po.order_line[0].visible_sequence,
            move1.sequence,
            "The Sequence of the Purchase Order Lines does not "
            "match to the Stock Moves",
        )
        self.assertEqual(
            po.order_line[1].visible_sequence,
            move2.sequence,
            "The Sequence of the Purchase Order Lines does not "
            "match to the Stock Moves",
        )

    def test_purchase_order_line_sequence_with_section_note(self):
        """
        Verify that the sequence is correctly assigned to the move associated
        with the purchase order line it references.
        """
        po = self._create_purchase_order()
        self.PurchaseOrderLine.create(
            {
                "name": "Section 1",
                "display_type": "line_section",
                "order_id": po.id,
                "product_qty": 0,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": self.product_id_1.name,
                "product_id": self.product_id_1.id,
                "product_qty": 15.0,
                "product_uom": self.product_id_1.uom_po_id.id,
                "price_unit": 150.0,
                "date_planned": datetime.today(),
                "order_id": po.id,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": "Note 1",
                "display_type": "line_note",
                "order_id": po.id,
                "product_qty": 0,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": self.product_id_2.name,
                "product_id": self.product_id_2.id,
                "product_qty": 1.0,
                "product_uom": self.product_id_2.uom_po_id.id,
                "price_unit": 50.0,
                "date_planned": datetime.today(),
                "order_id": po.id,
            }
        )
        po.button_confirm()
        moves = po.picking_ids[0].move_ids_without_package
        self.assertNotEqual(len(po.order_line), len(moves))
        for move in moves:
            self.assertEqual(move.sequence, move.purchase_line_id.visible_sequence)

    def test_write_purchase_order_line(self):
        """
        Verify that the sequence is correctly assigned to the move associated
        with the purchase order line it references when you modify it.
        """
        po = self._create_purchase_order()
        po.button_confirm()
        po.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_2.name,
                            "product_id": self.product_id_2.id,
                            "product_qty": 2,
                            "product_uom": self.product_id_2.uom_id.id,
                            "price_unit": 30,
                            "date_planned": datetime.today(),
                        },
                    )
                ]
            }
        )
        moves = po.picking_ids[0].move_ids_without_package
        for move in moves:
            self.assertEqual(move.sequence, move.purchase_line_id.visible_sequence)
