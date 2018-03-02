# -*- coding: utf-8 -*-
# © 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseOrderCancel(models.TransientModel):

    """ Ask a reason for the purchase order cancellation."""
    _name = 'purchase.order.cancel'
    _description = __doc__

    reason_id = fields.Many2one(
        'purchase.order.cancel.reason',
        string='Reason',
        required=True)

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        act_close = {'type': 'ir.actions.act_window_close'}
        purchase_ids = self._context.get('active_ids')
        if purchase_ids is None:
            return act_close
        assert len(purchase_ids) == 1, "Only 1 purchase ID expected"
        purchase = self.env['purchase.order'].browse(purchase_ids)
        purchase.cancel_reason_id = self.reason_id.id
        purchase.button_cancel()
        return act_close
