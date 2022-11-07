# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID
from odoo.tests.common import SavepointCase


class TestPurchaseRequestDestMove(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassProduct()
        cls.setUpClassPicking()
        cls.setUpClassPurchaseRequest()
        cls.create_rfq_wiz = cls.env["purchase.request.line.make.purchase.order"]

    @classmethod
    def setUpClassProduct(cls):
        cls.product1 = cls.env.ref("product.product_product_13")
        cls.product2 = cls.env.ref("product.product_product_16")
        cls.products = cls.product1 | cls.product2
        cls.products.purchase_request = True

    @classmethod
    def setUpClassPicking(cls):
        picking = cls.env.ref("stock.outgoing_shipment_main_warehouse")
        cls.move_model = cls.env["stock.move"]
        cls.picking = picking.copy({"move_lines": [], "move_line_ids": []})
        cls.location = cls.picking.location_id
        cls.move1 = cls.move_model.create(
            {
                "name": cls.product1.display_name,
                "picking_id": cls.picking.id,
                "product_id": cls.product1.id,
                "product_uom_qty": 10,
                "product_uom": cls.product1.uom_id.id,
                "procure_method": "make_to_order",
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
            }
        )
        cls.move2 = cls.move_model.create(
            {
                "name": cls.product2.display_name,
                "picking_id": cls.picking.id,
                "product_id": cls.product2.id,
                "product_uom_qty": 10,
                "product_uom": cls.product2.uom_id.id,
                "procure_method": "make_to_order",
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
            }
        )
        cls.moves = cls.move1 | cls.move2

    @classmethod
    def setUpClassPurchaseRequest(cls):
        cls.purchase_request_model = cls.env["purchase.request"]
        cls.purchase_request_line_model = cls.env["purchase.request.line"]
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        vals = {
            "picking_type_id": cls.picking_type_in.id,
            "requested_by": SUPERUSER_ID,
        }
        cls.purchase_request = cls.purchase_request_model.create(vals)
        cls.request_line1 = cls.purchase_request_line_model.create(
            {
                "request_id": cls.purchase_request.id,
                "product_id": cls.move1.product_id.id,
                "product_uom_id": cls.move1.product_id.uom_id.id,
                "product_qty": cls.move1.product_uom_qty,
                "move_dest_ids": [(4, cls.move1.id, 0)],
            }
        )
        cls.request_line2 = cls.purchase_request_line_model.create(
            {
                "request_id": cls.purchase_request.id,
                "product_id": cls.move2.product_id.id,
                "product_uom_id": cls.move2.product_id.uom_id.id,
                "product_qty": cls.move2.product_uom_qty,
                "move_dest_ids": [(4, cls.move2.id, 0)],
            }
        )

    def add_stock_for_product(self, products, qty):
        quant_model = self.env["stock.quant"]
        for product in products:
            quant_model._update_available_quantity(product, self.location, qty)

    def test_purchase_request_cancel(self):
        # If we reject a PR, related moves should pick goods from stock
        self.purchase_request.button_rejected()
        self.add_stock_for_product(self.products, 10)
        self.picking.action_assign()
        for move in self.moves:
            self.assertEqual(move.reserved_availability, 10)
            self.assertEqual(move.state, "assigned")

    def test_purchase_request_done(self):
        self.purchase_request.button_done()
        self.add_stock_for_product(self.products, 10)
        self.picking.action_assign()
        for move in self.moves:
            self.assertEqual(move.reserved_availability, 10)
            self.assertEqual(move.state, "assigned")

    def _spawn_wiz(self, lines):
        vals = {"supplier_id": self.env.ref("base.res_partner_12").id}
        context = {
            "active_model": "purchase.request.line",
            "active_ids": lines.ids,
        }
        return self.create_rfq_wiz.with_context(context).create(vals)

    def test_purchase_request_partially_cancelled(self):
        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()
        # Create a purchase order for only 1 on the 2 purchase lines
        wiz = self._spawn_wiz(self.request_line1)
        wiz.make_purchase_order()
        # only request1 has a purchase line
        self.assertTrue(self.request_line1.purchase_lines)
        self.assertFalse(self.request_line2.purchase_lines)
        # Now set PR as cancel
        self.purchase_request.button_rejected()
        # Both moves are `make_to_stock` and shouldn't wait for a purchase_order
        self.assertEqual(self.move1.procure_method, "make_to_stock")
        self.assertEqual(self.move2.procure_method, "make_to_stock")
        # Receive stock for both products
        self.add_stock_for_product(self.products, 10)
        # We do not case anymore about the created PO, we should be able to assign
        # goods
        self.picking.action_assign()
        # Both move1 and move2 are assigned.
        self.assertEqual(self.move2.reserved_availability, 10)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move1.reserved_availability, 10)
        self.assertEqual(self.move1.state, "assigned")
        # however, if we unreject the PR, moves should be back to `make_to_order`
        self.purchase_request.button_draft()
        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()
        self.picking.do_unreserve()
        self.picking.action_assign()
        # Both move1 and move2 are waiting for another operation
        self.assertEqual(self.move2.reserved_availability, 0)
        self.assertEqual(self.move2.state, "waiting")
        self.assertEqual(self.move2.procure_method, "make_to_order")
        self.assertEqual(self.move1.reserved_availability, 0)
        self.assertEqual(self.move1.state, "waiting")
        self.assertEqual(self.move1.procure_method, "make_to_order")

    def test_purchase_request_partially_done(self):
        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()
        # Create a purchase order for only 1 on the 2 purchase lines
        wiz = self._spawn_wiz(self.request_line1)
        wiz.make_purchase_order()
        # only request1 has a purchase line
        self.assertTrue(self.request_line1.purchase_lines)
        self.assertFalse(self.request_line2.purchase_lines)
        purchase = self.request_line1.purchase_lines.order_id
        # Now set PR as done (TODO: Shouldn't be possible)
        self.purchase_request.button_done()
        # Receive stock for both products
        self.add_stock_for_product(self.products, 10)
        # Reserve goods
        self.picking.action_assign()
        self.assertEqual(self.move1.created_purchase_line_id, purchase.order_line)
        self.assertEqual(purchase.order_line.move_dest_ids, self.move1)
        # Only move for product2 is assigned
        self.assertEqual(self.move2.reserved_availability, 10)
        self.assertEqual(self.move2.state, "assigned")
        # But move1 is waiting for another operation
        self.assertEqual(self.move1.reserved_availability, 0.0)
        self.assertEqual(self.move1.state, "waiting")
        self.assertEqual(self.move1.procure_method, "make_to_order")
        # Now, process the purchase.
        # Approve it, confirm it.
        purchase.button_approve()
        purchase.button_confirm()
        # Receive goods
        incoming_picking = purchase.picking_ids
        incoming_picking.action_assign()
        # should be only 1 move line here
        incoming_move_line = incoming_picking.move_line_ids
        incoming_move_line.qty_done = incoming_move_line.product_uom_qty
        incoming_picking.button_validate()
        # Then, try to reserve goods again.
        self.picking.action_assign()
        # Both move1 and move2 are assigned.
        self.assertEqual(self.move2.reserved_availability, 10)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move1.reserved_availability, 10)
        self.assertEqual(self.move1.state, "assigned")
