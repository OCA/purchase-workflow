##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Constant Values
    _TARGET_TYPE = [
        ('product_price_inv_eq', '€'),
        ('time', 'days'),
        ('weight', 'kg'),
    ]

    # Columns Section
    purchase_target = fields.Integer()
    target_type = fields.Selection(
        _TARGET_TYPE, required=True,
        default='product_price_inv_eq',
        help="""This defines the amount of products you want to"""
        """ purchase. \n"""
        """The system will compute a purchase order based on the stock"""
        """ you have and the average consumption of each product."""
        """* Target type '€': computed purchase order will cost"""
        """ at least the amount specified\n"""
        """* Target type 'days': computed purchase order will last at"""
        """ least the number of days specified (according to current"""
        """ average consumption)\n"""
        """* Target type 'kg': computed purchase order will weight"""
        """ at least the weight specified""")
    cpo_line_order_field = fields.Selection(
        [
            ('product_code', 'Supplier Product Code'),
            ('product_name', 'Supplier Product Name'),
            ('product_sequence', 'Product Sequence'),
        ],
        string='CPO Lines Order',
        help='The field used to sort the CPO lines',
        default='product_code',
        required=True,
    )

    cpo_line_order = fields.Selection(
        [
            ('asc', 'Ascending'),
            ('desc', 'Descending'),
        ],
        string='CPO Lines Order Direction',
        default='asc',
        required=True,
    )
