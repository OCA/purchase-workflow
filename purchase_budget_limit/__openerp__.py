# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
    'name': "Block over-budget Purchase Orders",
    'version': '1.1',
    'author': u'Numérigraphe SARL',
    'category': 'Purchase Management',
    'description': '''
Let Budget managers define limits on Purchase Orders
====================================================

When new Purchase Orders are being confirmed, this module will put them in a
special state if the remaining budget is not sufficient to pay the expected
invoice in one of the Budget Lines in the same period.

Purchase managers can :
- either wait until the financial situation changes
- or override the budget and approve the Purchase Order
- or cancel the Purchase Order.
''',
    'depends': ['account_budget', 'purchase'],
    'data': [
        'purchase_workflow.xml',
        'purchase_view.xml',
        'wizard/purchase_budget_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [
        # TODO add an automatic test:
        # - create a budget line for 10000 EUR
        # - create a PO for 100 EUR and validate it, check it's not blocked
        # - create a budget line for 150 EUR
        # - create a PO for 200 EUR and validate it, check it's blocked
        # - override the budget and check the PO is validated
    ]
}
