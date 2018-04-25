# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    created_purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        'Created Purchase Request Line',
        ondelete='set null', readonly=True, copy=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(
            StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields += ['created_purchase_request_line_id']
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(
            StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted += [move.purchase_line_id.id,
                        move.created_purchase_request_line_id.id]
        return keys_sorted

    def _action_cancel(self):
        for move in self:
            if move.created_purchase_request_line_id:
                try:
                    activity_type_id = self.env.ref(
                        'mail.mail_activity_data_todo').id
                except ValueError:
                    activity_type_id = False
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type_id,
                    'note': _('A sale/manufacturing order that generated this '
                              'purchase request has been cancelled/deleted. '
                              'Check if an action is needed.'),
                    'user_id':
                        move.created_purchase_request_line_id.
                        product_id.responsible_id.id,
                    'res_id':
                        move.created_purchase_request_line_id.request_id.id,
                    'res_model_id': self.env.ref(
                        'purchase_request.model_purchase_request').id,
                })
        return super(StockMove, self)._action_cancel()
