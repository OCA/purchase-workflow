# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = 'New'
        return super(PurchaseOrder, self).copy(default=default)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.rfq') or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            rfq = order.name
            order.write({
                'origin': rfq,
                'name': self.env['ir.sequence'].next_by_code(
                    'purchase.order')
            })
        return res
