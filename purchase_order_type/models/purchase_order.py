# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api
from openerp.addons.purchase.purchase import purchase_order


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.onchange('order_type')
    def onchange_order_type(self):
        self.invoice_method = self.order_type.invoice_method

    def _get_order_type(self):
        return self.env['purchase.order.type'].search([])[:1].id

    @api.multi
    def onchange_partner_id(self, part):
        res = super(PurchaseOrder, self).onchange_partner_id(part)
        if part:
            partner = self.env['res.partner'].browse(part)
            res['value'].update({
                'order_type': partner.purchase_type.id
                or self._get_order_type(),
            })
        return res

    order_type = fields.Many2one(comodel_name='purchase.order.type',
                                 readonly=False,
                                 states=purchase_order.READONLY_STATES,
                                 string='Type',
                                 ondelete='restrict',
                                 default=_get_order_type)
