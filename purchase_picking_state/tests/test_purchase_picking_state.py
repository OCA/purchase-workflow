# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPurchasePickingState(TransactionCase):
    def test_picking_state_in_purchase_order(self):
        for purchase in self.env['purchase.order'].search([]):
            if not purchase.picking_ids:
                self.purchase_draft = purchase
            else:
                pickings_state = set(
                    [picking.state for picking in purchase.picking_ids])
                if pickings_state == set(['cancel']):
                    self.purchase_cancel = purchase
                elif (pickings_state == set(['cancel', 'done']) or
                      pickings_state == set(['done'])):
                    self.purchase_done = purchase
                elif 'done' in pickings_state:
                    self.purchase_partially_received = purchase
                else:
                    self.purchase_not_received = purchase
        self.assertEquals(self.purchase_draft.picking_state, 'draft')
        self.assertEquals(self.purchase_cancel.picking_state, 'cancel')
        self.assertEquals(self.purchase_done.picking_state, 'done')
        self.assertEquals(self.purchase_partially_received.picking_state,
                          'partially_received')
        self.assertEquals(self.purchase_not_received.picking_state,
                          'not_received')
