# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier <guewen.baconnier@camptocamp.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class PurchaseOrderType(models.Model):
    _name = 'purchase.order.type'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    incoterm_id = fields.Many2one(comodel_name='stock.incoterms',
                                  string='Incoterm')
    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type', string='Deliver To',
        domain="[('code', '=', 'incoming')]")
