# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    """Adds one_agreement_per_product field on company"""

    _inherit = "res.company"

    one_agreement_per_product = fields.Boolean(
        'One agreement per product',
        help='If checked you can have only'
        ' one framework agreement'
        ' per product at the same time.'
    )
