# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(PurchaseOrder, self).copy(default=default)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.rfq') or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def wkf_confirm_order(self):
        if super(PurchaseOrder, self).wkf_confirm_order():
            for purchase in self:
                rfq = purchase.name
                purchase.write({
                    'origin': rfq,
                    'name': self.env['ir.sequence'].next_by_code(
                        'purchase.order')
                })
        return True
