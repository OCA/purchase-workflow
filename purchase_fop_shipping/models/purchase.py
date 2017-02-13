# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import Warning as UserError
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"
    fop_reached = fields.Boolean(
        string='FOP reached',
        help='Free-Of-Payment shipping reached',
        compute='_fop_shipping_reached')
    force_order_under_fop = fields.Boolean(
        string='Confirm under FOP',
        help='Force confirm purchase order under Free-Of-Payment shipping',)
    fop_shipping = fields.Float(
        'FOP shipping',
        related='partner_id.fop_shipping',
        readonly=True,
        help='Min purchase order amount for Free-Of-Payment shipping',)

    @api.multi
    @api.depends('amount_total', 'partner_id.fop_shipping')
    def _fop_shipping_reached(self):
        for record in self:
            record.fop_reached = record.amount_total >\
                record.partner_id.fop_shipping

    @api.multi
    def button_approve(self, force=False):
        for po in self:
            if not po.force_order_under_fop and not po.fop_reached:
                raise UserError(
                    _('You cannot confirm a purchase order with amount under '
                      'FOP shipping. To force confirm you must belongs to "FOP'
                      ' shipping Manager".'))
        result = super(PurchaseOrder, self).button_approve(force=force)
        return result
