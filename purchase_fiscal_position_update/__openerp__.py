# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase Fiscal Position Update module for Odoo
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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
    'name': 'Purchase Fiscal Position Update',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': 'Changing the fiscal position of a purchase order will '
    'auto-update purchase order lines',
    'description': """
Purchase Fiscal Position Update
===============================

With this module, when a user changes the fiscal position of a purchase order,
the taxes on all the purchase order lines which have a product are
automatically updated. The purchase order lines without a product are not
updated and a warning is displayed to the user in this case.
""",
    'author': "Julius Network Solutions,"
              "Akretion,"
              "Odoo Community Association (OCA)",
    'depends': ['purchase'],
    'data': [],
    'installable': True,
}
