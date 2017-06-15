# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_vci = fields.Boolean('Vendor Consignment Inventory')

    @api.multi
    def _create_picking(self):
        for order in self:
            if not order.is_vci:
                super(PurchaseOrder, order)._create_picking()
        return True
