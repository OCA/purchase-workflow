# -*- coding: utf-8 -*-
# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        """
        the propagate field in purchases is not informed in any case, so it will always be true
        therefore when we cancel a mto purchase the picking from the sale is cancelled
        what this does: if the move comes from another one, search the rule that generated it and apply its propagate
        """
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if res and self.move_dest_ids:
            rule = self.env['procurement.group']._get_rule(
                self.product_id, self.order_id.picking_type_id.default_location_dest_id,
                {'route_ids': self.order_id.picking_type_id.warehouse_id.route_ids,
                 'warehouse_id': self.order_id.picking_type_id.warehouse_id}
            )
            if rule:
                res[0]['propagate'] = rule.propagate
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_cancel(self):
        """
        upon cancelling the move, if the cancelation is not propagated, the original moves are left in the same state
        so the moves from the sale will be "waiting for another operation", when they have been changed to mts
        what this does: recompute the state of the affected moves
        """
        moves_to_recompute = self.mapped('order_line.move_dest_ids')
        res = super(PurchaseOrder, self).button_cancel()
        moves_to_recompute._recompute_state()
        return res
