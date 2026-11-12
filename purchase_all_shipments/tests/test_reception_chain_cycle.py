# Copyright 2026 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestReceptionChainCycle(TransactionCase):
    def test_reception_chain_cycle_no_recursion(self):
        """A cycle in ``move_dest_ids`` must not raise RecursionError.

        Returning a return links the forward and backward moves to each other,
        so the pushed reception chain becomes circular. Computing the chain
        used to recurse infinitely over that graph.
        """
        warehouse = self.env.ref("stock.warehouse0")
        product = self.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        push_rule = self.env["stock.rule"].create(
            {
                "name": "Test push rule",
                "action": "push",
                "picking_type_id": warehouse.in_type_id.id,
                "location_src_id": warehouse.wh_input_stock_loc_id.id,
                "location_dest_id": warehouse.lot_stock_id.id,
                "route_id": warehouse.reception_route_id.id,
            }
        )
        move_vals = {
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "product_uom": product.uom_id.id,
            "location_id": warehouse.wh_input_stock_loc_id.id,
            "location_dest_id": warehouse.lot_stock_id.id,
            "rule_id": push_rule.id,
        }
        move_a = self.env["stock.move"].create(dict(move_vals, name="A"))
        move_b = self.env["stock.move"].create(dict(move_vals, name="B"))
        # Build the cycle: A -> B -> A.
        move_a.move_dest_ids = [(6, 0, move_b.ids)]
        move_b.move_dest_ids = [(6, 0, move_a.ids)]
        # Must not raise RecursionError and must collect each move once.
        self.assertEqual(move_a._get_reception_chain_moves(), move_a | move_b)
