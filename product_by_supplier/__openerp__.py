# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: LIN Yu <lin.yu@elico-corp.com>
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
    'name': 'Product by supplier info',
    'version': '1.0',
    'category': 'purchase',
    'sequence': 19,
    'summary': 'Show products grouped by suppliers',
    'description': """
This module categorizes each product item by supplier.
======================================================
* It allows for users to be able to view a compiled list of products supplied \
by the supplier.
* Users can also directly add new products to the supplier's list.
    """,
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'images': [
               'static/images/product_supplier_info.png'
               ],
    'depends': ['product', 'stock'],
    'data': [
        'product_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
