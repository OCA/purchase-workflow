# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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
    'name': "Purchase delivery terms",
    'version': '0.2',
    'category': 'Purchase Management',
    'summary': "Delivery term for purchase orders",
    'description': """
Delivery term for purchase orders.
You can configure delivery terms specifying the quantity percentage and the
delay for every term line.  You can then associate the term to the 'main'
order line and generate the 'detailed' order lines which in turn will
generate several pickings according to delivery term (thanks to
'purchase_multi_picking' module).
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['purchase_multi_picking'],
    "data": [
        'purchase_view.xml',
        'security/ir.model.access.csv',
        'purchase_data.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
