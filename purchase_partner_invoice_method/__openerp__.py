# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase Partner Invoice Method module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
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
    'name': 'Purchase Partner Invoice Method',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': "Adds supplier invoicing control on partner form",
    'description': """
This module adds a new field on the partner form in the *Accouting* tab:
*Supplier Invoicing Control*. The value of this field will be used when you
create a new Purchase Order with this partner as supplier.

This module has been written by Alexis de Lattre
<alexis.delattre@akretion.com>
    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'depends': ['purchase'],
    'data': ['partner_view.xml'],
    'demo': ['partner_demo.xml'],
    'installable': True,
}
