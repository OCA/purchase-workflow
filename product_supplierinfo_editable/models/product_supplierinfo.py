# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_editable = fields.Boolean(string='Is editable',
                                 compute='_compute_is_editable',
                                 default=True)

    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = True
