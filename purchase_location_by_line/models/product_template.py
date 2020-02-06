# Copyright 2020 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_location_dest_id = fields.Many2one(
        comodel_name='stock.location', string='Default Destination',
        help='The default destination location that will appear '
             'on the purchase order line.',
        domain=[('usage', 'in', ['internal', 'transit'])])
