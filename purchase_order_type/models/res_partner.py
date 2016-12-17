# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier <guewen.baconnier@camptocamp.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_type = fields.Many2one(
        comodel_name='purchase.order.type', string='Purchase Order Type')
