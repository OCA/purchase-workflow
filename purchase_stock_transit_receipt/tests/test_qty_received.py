# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TransitReceiptCommon


class TestQtyReceived(TransitReceiptCommon):
    def _return(self, picking, quantity, location_dest=None):
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        wizard.product_return_moves.quantity = quantity
        return_picking = self.env["stock.picking"].browse(
            wizard.action_create_returns()["res_id"]
        )
        if location_dest:
            return_picking.location_dest_id = location_dest
            return_picking.move_ids.location_dest_id = location_dest
        self._validate(return_picking)
        return return_picking

    def test_received_at_physical_receipt(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        self.assertEqual(purchase.order_line.qty_received, 0)
        self._validate(self._next_picking(transit_receipt))
        self.assertEqual(purchase.order_line.qty_received, 5)
        self.assertEqual(purchase.picking_ids, transit_receipt)

    def test_partial_physical_receipt(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self._validate(physical_receipt, quantity=2)
        self.assertEqual(purchase.order_line.qty_received, 2)
        backorder = physical_receipt.backorder_ids
        self.assertTrue(backorder)
        self._validate(backorder)
        self.assertEqual(purchase.order_line.qty_received, 5)
        self.assertEqual(purchase.picking_ids, transit_receipt)

    def test_return_physical_receipt(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self._validate(physical_receipt)
        return_picking = self._return(physical_receipt, 2)
        self.assertEqual(
            return_picking.location_dest_id,
            self.warehouse.incoming_transit_location_id,
        )
        self.assertEqual(purchase.order_line.qty_received, 3)
        self._return(return_picking, 2)
        self.assertEqual(purchase.order_line.qty_received, 5)

    def test_return_transit_receipt(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        return_picking = self._return(transit_receipt, 2)
        self.assertEqual(
            return_picking.location_dest_id,
            self.env.ref("stock.stock_location_suppliers"),
        )
        self.assertEqual(purchase.order_line.qty_received, 0)
        self._validate(physical_receipt, quantity=3)
        self.assertEqual(purchase.order_line.qty_received, 3)

    def test_transit_receipt_received_again(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        vendor_return = self._return(transit_receipt, 2)
        receipt_again = self._return(
            vendor_return, 2, self.warehouse.incoming_transit_location_id
        )
        outgoing_moves, incoming_moves = (
            purchase.order_line._get_outgoing_incoming_moves()
        )
        self.assertEqual(outgoing_moves, vendor_return.move_ids)
        self.assertIn(receipt_again.move_ids, incoming_moves)
        self.assertEqual(purchase.order_line.qty_received, 0)

    def test_two_steps(self):
        self.warehouse.reception_steps = "two_steps"
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self._validate(physical_receipt)
        self.assertEqual(purchase.order_line.qty_received, 5)
        self._validate(self._next_picking(physical_receipt))
        self.assertEqual(purchase.order_line.qty_received, 5)

    def test_purchase_without_transit(self):
        purchase = self._create_purchase(self.warehouse.in_type_id)
        receipt = purchase.picking_ids
        self._validate(receipt, quantity=2)
        self.assertEqual(purchase.order_line.qty_received, 2)
        self._return(receipt, 1)
        self.assertEqual(purchase.order_line.qty_received, 1)
