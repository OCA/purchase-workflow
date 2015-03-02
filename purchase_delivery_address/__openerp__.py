# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
{'name': 'Purchase Delivery Address',
 'summary': 'Allows to manage the delivery address on a purchase',
 'version': '1.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Purchase Management',
 'license': 'AGPL-3',
 'complexity': 'easy',
 'images': [],
 'depends': ['purchase',
             'sale_stock',
             ],
 'demo': [],
 'data': ['view/purchase_order.xml',
          'view/stock_picking.xml',
          ],
 'auto_install': False,
 'test': [
     'test/setup_user.yml',
     'test/setup_product.yml',
     'test/setup_dropshipping.xml',
     'test/test_propagate_address.yml',
 ],
 'installable': True,
 }
