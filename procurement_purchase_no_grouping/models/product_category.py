# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    procured_purchase_grouping = fields.Selection(
        [('standard', 'Standard grouping'),
         ('line', 'No line grouping'),
         ('order', 'No order grouping'),
         ('product_category', 'Product category grouping')],
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
             "* Product category grouping: This option groups products in the "
             "same purchase order that belongs to the same product category.")
