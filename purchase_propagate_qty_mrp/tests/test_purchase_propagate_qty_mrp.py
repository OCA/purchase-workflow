# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestQtyUpdate(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Product = cls.env["product.product"]
        cls.seller = cls.env["res.partner"].create({"name": "supplier"})
        # Create a kit
        cls.product_bed_with_curtain = cls.Product.create(
            {
                "name": "BED WITH CURTAINS",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": False,
            }
        )
        cls.product_bed_structure = cls.Product.create(
            {
                "name": "BED STRUCTURE",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 50.0})],
            }
        )
        cls.product_bed_curtain = cls.Product.create(
            {
                "name": "BED CURTAIN",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 10.0})],
            }
        )
        cls.bom_model = cls.env["mrp.bom"]
        # A kit that contains a bed and 2 curtains
        cls.bom_bed_with_curtain = cls.bom_model.create(
            {
                "product_tmpl_id": cls.product_bed_with_curtain.product_tmpl_id.id,
                "product_id": cls.product_bed_with_curtain.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.product_bed_curtain.id, "product_qty": 2.0},
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_bed_structure.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )

        cls.date_planned = "2024-11-04 12:00:00"
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.seller.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_bed_with_curtain.id,
                            "product_uom": cls.product_bed_with_curtain.uom_id.id,
                            "name": cls.product_bed_with_curtain.name,
                            "date_planned": cls.date_planned,
                            "product_qty": 42.0,
                            "price_unit": 300.0,
                        },
                    ),
                ],
            }
        )
        cls.po.button_confirm()

    def _check_moves_quantity(self, moves, values):
        """Quick check of moves and their planned quantity."""
        for move in moves:
            if move.state == "done":
                continue
            self.assertEqual(move.product_uom_qty, values[move.product_id])

    def _receive_kit(self, purchase_line, quantity_receive, partially=False):
        """Process the reception of a kit quantity in relation to a purchase line.

        If partially is set, the quantity of the 2nd component will be divided by half.
        Making a partial reception of the kit.

        """
        move1 = purchase_line.move_ids.filtered(
            lambda r: r.product_id == self.product_bed_structure
        )
        new_move_vals = move1._split(quantity_receive)
        new_move_1 = self.env["stock.move"].create(new_move_vals)
        new_move_1._action_confirm(merge=False)
        new_move_1._action_assign()
        new_move_1.quantity_done = quantity_receive
        new_move_1._action_done()
        move2 = purchase_line.move_ids.filtered(
            lambda r: r.product_id == self.product_bed_curtain
        )
        receiving = 0
        if partially:
            receiving = quantity_receive
        else:
            receiving = quantity_receive * 2
        new_move_vals = move2._split(receiving)
        new_move_2 = self.env["stock.move"].create(new_move_vals)
        new_move_2._action_confirm(merge=False)
        new_move_2._action_assign()
        new_move_2.quantity_done = receiving
        new_move_2._action_done()

    def test_purchase_line_qty_decrease_allowed(self):
        """Check decreasing ordered quantity to less than what is left to receive.

        Purchased 42 kits
        Received nothing yet
        Update the purchase quantity to 25

        """
        po_line = self.po.order_line[0]
        moves = po_line.move_ids
        po_line.write({"product_qty": 25})
        self._check_moves_quantity(
            moves, {self.product_bed_structure: 25, self.product_bed_curtain: 50}
        )

    def test_purchase_line_qty_decrease_not_allowed(self):
        """Check decreasing the quantity to more than what is left to receive.

        Purchased 42 kits
        Receive 30 of them
        Update the purchase quantity to 29 -> not allowed

        """
        po_line = self.po.order_line[0]
        self._receive_kit(po_line, 30)
        moves = po_line.move_ids
        self._check_moves_quantity(
            moves, {self.product_bed_structure: 12, self.product_bed_curtain: 24}
        )
        # Exception raised by Odoo standard
        with self.assertRaises(UserError):
            po_line.write({"product_qty": 29})

    def test_decrease_purchase_qty_nothing_left_to_receive(self):
        """Check decreasing the quantity to the exact amount that has been received.

        Purchased 42 kits
        Received 30
        Update the purchase quantity to 30 -> nothing left to receive

        """
        po_line = self.po.order_line[0]
        self._receive_kit(po_line, 30)
        moves = po_line.move_ids
        self._check_moves_quantity(
            moves, {self.product_bed_structure: 12, self.product_bed_curtain: 24}
        )
        po_line.write({"product_qty": 30})
        self._check_moves_quantity(
            moves, {self.product_bed_structure: 0, self.product_bed_curtain: 0}
        )

    def test_decrease_purchase_qty_allowed_partially_received_kit(self):
        """Check decrease quantity after partially receiving a kit.

        Purchased 42 kits
        Receive 14 kits and part of the 15th.
        Update the purchase quantity to 15 -> left part of a kit to receive
        """
        po_line = self.po.order_line[0]
        self._receive_kit(po_line, 15, partially=True)
        po_line.write({"product_qty": 15})
        moves = po_line.move_ids
        self._check_moves_quantity(
            moves, {self.product_bed_structure: 0, self.product_bed_curtain: 15}
        )

    def test_decrease_purchase_qty_not_allowed_partially_received_kit(self):
        """Check decrease quantity after partially receiving a kit.

        Purchased 42 kits
        Receive 14 kits and part of the 15th.
        Update the purchase quantity to 14 -> error raised
        """
        po_line = self.po.order_line[0]
        self._receive_kit(po_line, 15, partially=True)
        error = r".*remains to be done. For the kit BED STRUCTURE."
        with self.assertRaisesRegex(UserError, error):
            po_line.write({"product_qty": 14})
