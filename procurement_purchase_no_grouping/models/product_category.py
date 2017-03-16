# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    procured_purchase_grouping = fields.Selection(
        [('standard', 'Standard grouping'),
         ('line', 'No line grouping'),
         ('order', 'No order grouping'),
         ('one_sale_one_purchase', 'One sale, One purchase')],
        string='Procured purchase grouping', default='standard',
        help="Select the behaviour for grouping procured purchases for the "
             "the products of this category:\n"
             "* Standard grouping (default): Procurements will generate "
             "purchase orders as always, grouping lines and orders when "
             "possible.\n"
             "* No line grouping: If there are any open purchase order for "
             "the same supplier, it will be reused, but lines won't be "
             "merged.\n"
             "* No order grouping: This option will prevent any kind of "
             "grouping.\n"
             "* One sale, One purchase: This option group all lines for same"
             "suplier in one purchase order from the same sale order.")
