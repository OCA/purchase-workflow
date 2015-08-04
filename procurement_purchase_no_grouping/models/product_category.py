# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    group_on_procured_purchases = fields.Boolean(
        string='Group on procured purchases', default=True,
        help='If this new field is checked, running the procurement acts like'
        ' the standard way, adding the amount on existing line purchase order'
        ' if the product and the UoM is the same, but if it is not checked, no'
        ' grouping will be done, creating a new line each time')
