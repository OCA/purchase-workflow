# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier <guewen.baconnier@camptocamp.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons.purchase.purchase import PurchaseOrder as purchase_order


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _default_order_type(self):
        return self.env['purchase.order.type'].search([], limit=1)

    order_type = fields.Many2one(comodel_name='purchase.order.type',
                                 readonly=False,
                                 states=purchase_order.READONLY_STATES,
                                 string='Type',
                                 ondelete='restrict',
                                 default=_default_order_type)

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id_purchase_order_type(self):
        if self.partner_id.purchase_type:
            self.order_type = self.partner_id.purchase_type.id

    @api.onchange('order_type')
    def onchange_purchase_order_type(self):
        if self.order_type:
            if self.order_type.incoterm_id:
                self.incoterm_id = self.order_type.incoterm_id.id
            if self.order_type.picking_type_id:
                self.picking_type_id = self.order_type.picking_type_id.id
