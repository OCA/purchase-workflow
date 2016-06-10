# -*- coding: utf-8 -*-
##############################################################################
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
#
##############################################################################
from openerp import models, fields, api


class PickingImportWizard(models.TransientModel):
    _name = "picking.import.wizard"
    _description = "Import incoming shipment"

    @api.model
    def default_get(self, field_list):
        """Get pickings previously imported."""
        res = super(PickingImportWizard, self).default_get(field_list)
        if self.env.context.get('active_id') and 'prev_pickings' in field_list:
            distribution = self.env['purchase.cost.distribution'].browse(
                self.env.context['active_id'])
            pickings = self.env['stock.picking']
            moves = distribution.mapped('cost_lines.move_id')
            for line in distribution.cost_lines:
                if line.picking_id in pickings:
                    continue
                if all(x in moves for x in line.picking_id.move_lines):
                    pickings |= line.picking_id
            res['prev_pickings'] = [(6, 0, pickings.ids)]
        return res

    supplier = fields.Many2one(
        comodel_name='res.partner', string='Supplier', required=True,
        domain="[('supplier',  '=', True)]")
    pickings = fields.Many2many(
        comodel_name='stock.picking',
        relation='distribution_import_picking_rel', column1='wizard_id',
        column2='picking_id', string='Incoming shipments',
        domain="[('partner_id', 'child_of', supplier),"
               "('location_id.usage', '=', 'supplier'),"
               "('state', '=', 'done'),"
               "('id', 'not in', prev_pickings[0][2])]", required=True)
    prev_pickings = fields.Many2many(comodel_name='stock.picking')

    def _prepare_distribution_line(self, move):
        return {
            'distribution': self.env.context['active_id'],
            'move_id': move.id,
        }

    @api.multi
    def action_import_picking(self):
        self.ensure_one()
        distribution = self.env['purchase.cost.distribution'].browse(
            self.env.context['active_id'])
        previous_moves = distribution.mapped('cost_lines.move_id')
        for move in self.mapped('pickings.move_lines'):
            if move not in previous_moves:
                self.env['purchase.cost.distribution.line'].create(
                    self._prepare_distribution_line(move))
