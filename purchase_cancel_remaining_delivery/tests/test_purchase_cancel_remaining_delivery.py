# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SingleTransactionCase


class TestPurchaseCancelRemainingDelivery(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.purchase = cls.env.ref("purchase_stock.purchase_order_8")
        cls.purchase.button_confirm()

    def test_cancel_remaining_delivery(self):
        self.assertEqual(len(self.purchase.picking_ids), 1)
        for line in self.purchase.picking_ids.move_line_ids:
            # Partial reception to have a backorder
            line.qty_done = line.product_uom_qty - 1
        self.purchase.picking_ids._action_done()
        backorder_pick = self.purchase.picking_ids.filtered(
            lambda pick: pick.state != "done"
        )
        self.assertEqual(len(self.purchase.picking_ids), 2)
        self.assertEqual(backorder_pick.state, "assigned")
        self.purchase.button_cancel_remaining_delivery()
        self.assertEqual(backorder_pick.state, "cancel")
