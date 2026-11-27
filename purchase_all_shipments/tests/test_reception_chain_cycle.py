# Copyright 2026 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestReceptionChainCycle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.reception_steps = "two_steps"
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test vendor"})

    def _validate(self, picking):
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()

    def _return(self, picking):
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({"picking_id": picking.id})
        )
        for line in wizard.product_return_moves:
            line.quantity = line.move_id.product_uom_qty
        return_picking = self.env["stock.picking"].browse(
            wizard.action_create_returns()["res_id"]
        )
        self._validate(return_picking)
        return return_picking

    def test_return_of_return_does_not_recurse(self):
        """Returning a return must not break the order's reception chain.

        With a two-step reception, returning the pushed internal transfer and
        then returning that return makes the pushed moves point to each other
        through ``move_dest_ids``, so the reception chain becomes cyclic.
        Computing ``all_picking_ids`` used to recurse forever and the purchase
        order could no longer be opened.
        """
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "price_unit": 1.0,
                        },
                    )
                ],
            }
        )
        order.button_confirm()
        receipt = order.picking_ids.filtered(
            lambda p: p.picking_type_code == "incoming"
        )
        self._validate(receipt)
        internal = self.env["stock.picking"].search(
            [
                ("group_id", "=", order.group_id.id),
                ("picking_type_code", "=", "internal"),
                ("state", "not in", ("done", "cancel")),
            ]
        )
        self._validate(internal)
        return_picking = self._return(internal)
        return_of_return = self._return(return_picking)

        # Must not raise RecursionError and must list every related picking.
        order.invalidate_recordset()
        self.assertEqual(order.all_picking_count, 4)
        for picking in (receipt, internal, return_picking, return_of_return):
            self.assertIn(picking, order.all_picking_ids)
