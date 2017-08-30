# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import fields, models


class Procurement(models.Model):
    _inherit = 'procurement.order'

    request_id = fields.Many2one(
        comodel_name='purchase.request', ondelete='restrict',
        string='Latest Purchase Request', copy=False)
