#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _all_shipment_count(self):
        self.all_shipment_count = len(self.all_picking_ids)

    def _all_pickings(self):
        groups = self.mapped('picking_ids.move_lines.group_id')

        all_moves = self.env['stock.move'].search(
            [('group_id', 'in', groups.ids)]
        )
        self.all_picking_ids = all_moves.mapped('picking_id')

    @api.multi
    def view_all_picking(self):
        """Similar to the view_picking method in the purchase module"""
        action_data = self.env.ref('stock.action_picking_tree').read()[0]
        pickings = self.mapped('all_picking_ids')

        # override the context to get rid of the default filtering on
        # picking type
        action_data['context'] = {}

        # choose the view_mode accordingly
        if len(pickings) > 1:
            action_data['domain'] = [('id', 'in', pickings.ids)]
        else:
            form_view = self.env.ref('stock.view_picking_form')
            action_data['views'] = [(form_view.id, 'form')]
            action_data['res_id'] = pickings.id
        return action_data

    all_picking_ids = fields.One2many('stock.picking',
                                      string='All Shipments',
                                      compute='_all_pickings')
    all_shipment_count = fields.Integer('All Shipments',
                                        compute='_all_shipment_count')
