# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015
#    Francesco OpenCode Apruzzese (<f.apruzzese@apuliasoftware.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Purchase Order Secondary UoM",
    'version': '0.1',
    'category': 'Purchase',
    'author': 'Francesco OpenCode Apruzzese,Odoo Community Association (OCA)',
    'website': 'https://www.apuliasoftware.it',
    'license': 'AGPL-3',
    "depends": [
        'product',
        'purchase',
        ],
    "data": [
        'views/product_view.xml',
        'views/purchase_view.xml',
        ],
    "update_xml": [],
    "demo_xml": [],
    "auto_install": False,
    "installable": True
}
