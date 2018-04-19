"""
tests module Purchase Picking State
"""
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchasePickingState(TransactionCase):
    """
    Test Purchase Picking State
    """

    def test_picking_state(self):
        """
        test picking state in purchase order
        """
        draft_order_ids = self.env['purchase.order'].search([
            ('state', 'in', ['draft', 'sent', 'bid', 'cancel']),
        ])
        for purchase in draft_order_ids:
            self.assertEqual(purchase.picking_state, 'draft')
        confirmed_order_ids = self.env['purchase.order'].search([
            ('state', 'in', ['confirmed', 'approved', 'done']),
        ])
        for purchase in confirmed_order_ids:
            pickings_state = set(
                [picking.state for picking in purchase.picking_ids])
            if pickings_state == set(['cancel']):
                self.assertEqual(purchase.picking_state, 'cancel')
            elif (pickings_state == set(['cancel', 'done']) or
                  pickings_state == set(['done'])):
                self.assertEqual(purchase.picking_state, 'done')
            elif 'done' in pickings_state:
                self.assertEqual(purchase.picking_state, 'partially_received')
            else:
                self.assertEqual(purchase.picking_state, 'not_received')
