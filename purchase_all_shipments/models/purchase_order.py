# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    all_picking_ids = fields.One2many(
        string='All Pickings',
        comodel_name='stock.picking',
        compute='_compute_all_pickings',
    )
    all_picking_count = fields.Integer(
        string='All Pickings',
        compute='_compute_all_pickings',
    )

    @api.depends('picking_ids')
    def _compute_all_pickings(self):
        for rec in self:
            groups = rec.mapped('picking_ids.move_lines.group_id')
            all_moves = rec.env['stock.move'].search(
                [('group_id', 'in', groups.ids)],
            )
            rec.all_picking_ids = all_moves.mapped('picking_id')
            rec.all_picking_count = len(rec.all_picking_ids)

    @api.multi
    def action_view_all_pickings(self):
        """Similar to the view_picking method in the purchase module"""
        self.ensure_one()
        action_data = self.env.ref('stock.action_picking_tree').read()[0]

        # override the context to get rid of the default filtering on
        # picking type
        action_data['context'] = {}

        # choose the view_mode accordingly
        if self.all_picking_count > 1:
            action_data['domain'] = [('id', 'in', self.all_picking_ids.ids)]
        else:
            form_view = self.env.ref('stock.view_picking_form')
            action_data['views'] = [(form_view.id, 'form')]
            action_data['res_id'] = self.all_picking_ids.id
        return action_data
