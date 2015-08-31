# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
    'name': 'Purchase Partner Order Policy',
    'version': '8.0.0.1.0',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': "Adds customer create invoice method on partner form",
    'description': """
    The module is similar to the policy for sales order. 
    A field is added to the type of provider policy. 
    Then in the purchase order, at select the provider the field Invoice Method is completed with the chosen policy.

    """,
    'author': "ADHOC SA",
    'website': 'www.adhoc.com.ar',
    'depends': ['purchase'],
    'data': ['partner_view.xml'],
    'demo': ['partner_demo.xml'],
    'installable': True,
    'auto_install': True,
    'application': False,
}
