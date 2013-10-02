# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
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
    'name': 'Purchase Landed Costs',
    'version': '0.8.1',
    'category': 'Warehouse Management',
    'description': """

    This module add the possibility to include landed costs in the average price computation.
    The landed costs can be defined for 
    * purchase orders
    costs defined for purchase orders and pickings will be distributed according to the distribution type
    defined in landed cost category
    * value - example custom fees
    * quantity - example freight
    for each landed cost position a draft invoice is created in validation of purchase order
    the products used to define landed cost must be classified "Distribution Type" as 
    ** "Value" (for customs) or 
    ** "Quantity" (for freight)

    Thanks to Savoir Faire Linux for their contributions on that module !
    """,
    'author': 'Camptocamp',
    'depends': ['purchase' ],
    'data_xml': ['security/ir.model.access.csv',
                   'purchase_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
