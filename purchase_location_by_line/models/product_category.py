# Copyright 2020 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    default_location_dest_id = fields.Many2one(
        comodel_name='stock.location', string='Default Destination',
        help='The default destination location that will appear '
             'on the purchase order line if not set on the product.',
        domain=[('usage', 'in', ['internal', 'transit'])])
