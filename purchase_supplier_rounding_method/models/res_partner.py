# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _SUPPLIER_ROUNDING_METHOD_SELECTION = [
        ('normal', 'Normal'),
        ('round_net_price', 'Round Net Price'),
    ]

    # Columns Section
    supplier_rounding_method = fields.Selection(
        selection=_SUPPLIER_ROUNDING_METHOD_SELECTION,
        string='Supplier Rounding Method', required=True, default='normal')
