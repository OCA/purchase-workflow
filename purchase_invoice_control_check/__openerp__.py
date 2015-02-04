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
    'name': "Purchase invoice control check",
    'version': '0.1',
    'category': 'Purchase Management',
    'summary': "Checks Invoicing Control in Purchase Orders "
               "during confirmation",
    'description': """
Purchase invoice control service
================================
This module aims to introduce checks that prevent users from confirming
purchase orders using a wrong Invoicing Control.

For example, currently a user can create a PO containing services and
set the invoice control 'Based on incoming shipments', and the application
does not prevent the user from doing that.

Then, the user has no option in the 'Invoice Control' menu to invoice that
line, and can only invoice based on a list of PO lines.

This modules introduces the following features:

Prevents a user from being able to confirm a Purchase Order with invoice
control 'Based on incoming shipments' that contains services.

Makes it possible to cancel a Purchase Order in which the user created the
PO containing services, with invoice control 'Based on incoming shipments'
(in order to correct the PO's that were created incorrectly before this
module was used).
""",
    'author': 'Eficent',
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['purchase'],
    "data": [
        'purchase_workflow.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
