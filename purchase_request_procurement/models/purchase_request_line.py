# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models


class PurchaseRequestLine(models.Model):

    _inherit = 'purchase.request.line'

    @api.multi
    def do_cancel(self):
        res = super(PurchaseRequestLine, self).do_cancel()
        procurements = self.mapped('procurement_id')
        procurements.with_context(
            from_purchase_request=True).cancel()
        if not self.env.context.get('cancel_procurement'):
            procurements.filtered(lambda r: r.state not in (
                'cancel', 'exception') and not r.rule_id.propagate).write({
                    'state': 'exception'})
            moves = procurements.filtered(
                lambda r: r.rule_id.propagate).mapped('move_dest_id')
            moves.filtered(lambda r: r.state != 'cancel').action_cancel()
        return res

    @api.multi
    def do_uncancel(self):
        """lines related to cancelled procurement remain cancelled."""
        lines = self.filtered(lambda l: l.procurement_id.state != 'cancel')
        res = super(PurchaseRequestLine, lines).do_uncancel()
        return res
