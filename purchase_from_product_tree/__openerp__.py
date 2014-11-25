# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase from product tree module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Purchase from Product tree',
    'version': '0.1',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': 'Wizard to create purchase orders from product variants',
    'description': """
This module adds a wizard on the product variants tree view to create
new purchase orders. Some companies don't want to use the re-ordering
rules to create purchase orders for some reasons (complexity, fast
changes in demand, etc...). Some companies may prefer to look at their
stock level and, from this analysis, decide which product variants they
need to re-order. This module implements this scenario.

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['purchase'],
    'data': ['wizard/purchase_from_product_view.xml'],
    'installable': True,
}
