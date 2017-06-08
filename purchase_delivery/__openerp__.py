# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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


{
    'name': 'Purchase Delivery Costs',
    'version': '1.0',
    'category': 'Purchase Management',
    'description': """
Allows you to add delivery methods in purchase orders and picking.
==============================================================

This module makes it possible to add delivery method to purchase orders and
can compute a shipping line in the purchase order or in the invoice when
created from an incoming shipment.

The application makes use of the same concepts of carrier and delivery grid
extending them as follows:
    * Introduces origin countries, states and ZIP in the delivery grid.
    * Uses the cost defined in the grid, instead of the sale price.
    * Uses the vendor address to match with the existing grid based on the
    origin information defined in the grid.
    * Uses the destination address (customer address for direct shipments
    and warehouse otherwise) to determine the grid, based on the destination
    parameters defined in the grid.

In case that the incoming shipment contains moves that have multiple
destination addresses, computes the average freight cost.
""",
    'author': 'Eficent',
    'depends': ['delivery', 'purchase'],
    'data': [
        'view/delivery_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
