from odoo import api, fields, models


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
        column2='picking_id', string='Incoming shipments', required=True)
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
