# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_picking_state(self):
        return [
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('not_received', 'Not Received'),
            ('partially_received', 'Partially Received'),
            ('done', 'Transferred'),
        ]

    @api.multi
    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_picking_state(self):
        for purchase in self:
            picking_state = 'draft'
            for picking in purchase.picking_ids:
                if picking_state in ['draft', 'cancel']:
                    if picking.state == 'cancel':
                        picking_state = 'cancel'
                    elif picking.state == 'done':
                        picking_state = 'done'
                    else:
                        picking_state = 'not_received'
                elif picking_state == 'done':
                    if picking.state == 'cancel':
                        picking_state = 'done'
                    elif picking.state == 'done':
                        picking_state = 'done'
                    else:
                        picking_state = 'partially_received'
                elif picking_state == 'not_received':
                    if picking.state == 'cancel':
                        picking_state = 'not_received'
                    elif picking.state == 'done':
                        picking_state = 'partially_received'
                    else:
                        picking_state = 'not_received'
                elif picking_state == 'partially_received':
                    if picking.state == 'cancel':
                        picking_state = 'partially_received'
                    elif picking.state == 'done':
                        picking_state = 'partially_received'
                    else:
                        picking_state = 'partially_received'
            purchase.picking_state = picking_state

    picking_state = fields.Selection(
        string="Picking status", readonly=True,
        compute='_compute_picking_state',
        selection='get_picking_state',
        help="Overall status based on all pickings")
