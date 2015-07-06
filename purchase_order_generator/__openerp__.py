# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Purchase Order Generator',
    'version': '0.1',
    'category': 'Management/Sales/Purchases',
    'summary': 'Configure the reception of products over a certain period of '
               'time',
    'author': ('Savoir-faire Linux',
               'Odoo Community Association (OCA)'),
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'purchase',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_generator_configuration.xml',
        'views/menus.xml',
        'wizard/purchase_order_generator.xml',
        'wizard/stock_transfer_details.xml',
    ],
    'demo': [
        'demo/purchase_order_generator_configuration.xml',
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
