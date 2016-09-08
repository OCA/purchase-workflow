# -*- coding: utf-8 -*-
# © 2016 Andrea Gallina @ Apulia Software S.r.l.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def get_move_state(self):
        return [
            ('draft', ''),
            ('cancel', _('Cancelled')),
            ('not_received', _('Not Received')),
            ('partially_received', _('Partially Received')),
            ('done', _('Transferred')),
        ]

    @api.multi
    @api.depends('move_ids', 'move_ids.state')
    def _compute_move_state(self):
        for purchase_line in self:
            if purchase_line.move_ids:
                move_state = set(
                    [picking.state for picking in purchase_line.move_ids])
                if move_state == set(['cancel']):
                    purchase_line.picking_state = 'cancel'
                elif (move_state == set(['cancel', 'done']) or
                      move_state == set(['done'])):
                    purchase_line.move_state = 'done'
                elif 'done' in move_state:
                    purchase_line.move_state = 'partially_received'
                else:
                    purchase_line.move_state = 'not_received'
            else:
                purchase_line.move_state = 'draft'

    move_state = fields.Selection(
        string="Move status", readonly=True,
        compute='_compute_move_state',
        selection='get_move_state',
        help="Overall status based on all moves")
