# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, api


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(purchase_order, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.supplier_order_policy:
                res['value']['invoice_method'] = \
                    partner.supplier_order_policy
        return res
