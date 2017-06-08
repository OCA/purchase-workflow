# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Ecosoft (<http://www.ecosoft.co.th>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Purchase - Separate Quote and Order',
    'version': '10.0.0.1.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Purchase',
    'description': """
This module separate quotation and purchase order
by adding order_type as 'quotation' or 'purchase_order' in purchase.order model.

Quotation will have only 2 state, Draft and Done.
Purchase Order state will be as normal.
    """,
    'website': 'http://ecosoft.co.th',
    'depends': ['purchase', ],
    'images': [],
    'data': [
        'data/ir_sequence_data.xml',
        'views/purchase_view.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
