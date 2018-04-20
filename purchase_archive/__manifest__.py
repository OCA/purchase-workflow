# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Purchase Archive",
    "summary": "Allows to archive Purchase Orders in state draft, done or "
               "cancelled, and removes rights to delete them.",
    "version": "11.0.1.0.0",
    "depends": [
        "purchase"
    ],
    "author": "brain-tec AG,"
              "Odoo Community Association (OCA)",
    "category": "Purchase",
    "website": "http://www.braintec-group.com",
    'license': 'AGPL-3',
    "data": ['views/purchase_views_ext.xml',
             'security/ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
}

