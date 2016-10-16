# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_picking_state(self):
        return [
            ('draft', ''),
            ('cancel', 'Cancelled'),
            ('not_received', 'Not Received'),
            ('partially_received', 'Partially Received'),
            ('done', 'Transferred'),
        ]

    @api.multi
    def _compute_picking_state(self):
        for purchase in self:
            if purchase.picking_ids:
                pickings_state = set(
                    [picking.state for picking in purchase.picking_ids])
                if pickings_state == set(['cancel']):
                    purchase.picking_state = 'cancel'
                elif (pickings_state == set(['cancel', 'done']) or
                      pickings_state == set(['done'])):
                    purchase.picking_state = 'done'
                elif 'done' in pickings_state:
                    purchase.picking_state = 'partially_received'
                else:
                    purchase.picking_state = 'not_received'
            else:
                purchase.picking_state = 'draft'

    picking_state = fields.Selection(
        string="Picking status", readonly=True,
        compute='_compute_picking_state',
        selection='get_picking_state',
        help="Overall status based on all pickings")
