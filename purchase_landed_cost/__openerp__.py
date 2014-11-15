# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
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
    'name': 'Purchase landed costs - Alternative option',
    'version': '1.0',
    'author': 'Joaquin Gutierrez, OdooMRP team',
    'category': 'Purchase Management',
    'website': 'http://www.gutierrezweb.es,http://www.odoomrp.com',
    'summary': 'Purchase cost distribution',
    'description': """
This module manages your purchase expenses
==========================================

The functionality of this module is to provide a way to manage your purchase
costs more easily than the official module (stock_landed_cost) and allow to
distribute them with a lot of methods.

Main features:
--------------
* Possibility to assign landed cost afterwards in a separate screen.
* Management of expense types with preconfigured calculation methods.
* Distribution of costs based on weight, volume, product price, etc.
* Types marked as default are automatically added to each new purchase
  distribution.
* Management orders shopping expenses associated with one or more entry slips.
* Upgrade cost price of products based on the costs.
* Currently only one type of upgrade cost is available: direct upgrade.

To-do:
------
* Ability to add expenses in multi currency.
* Purchase distribution report.

Icon:
-----
Thanks to Visual Pharm http://icons8.com
""",

    'depends': [
        'stock',
        'purchase',
    ],
    'data': [
        'wizard/picking_import_wizard_view.xml',
        'wizard/import_invoice_line_wizard_view.xml',
        'views/purchase_cost_distribution_view.xml',
        'views/purchase_expense_type_view.xml',
        'data/purchase_cost_distribution_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'images': [
        '/static/description/images/purchase_order_expense_main.png',
        '/static/description/images/purchase_order_expense_line.png',
        '/static/description/images/expenses_types.png',
    ],
}
