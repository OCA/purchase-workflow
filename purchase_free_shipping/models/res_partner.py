# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    free_shipping_amount = fields.Float(string='Free Shipping Minimum Amount',
                                        company_dependent=True)
