# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

{'name': 'Purchase Supplier Postage Free',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Purchase Management',
 'depends': ['purchase',
             ],
 'description': """
Purchase Supplier Postage Free
==============================

* Add a field "Postage free above amount" on the suppliers, which is an
  optional amount above which the supplier does not charge the shipping
  fees.
* Display this amount on the purchase orders as an indication
* Add a filter on the purchase orders showing the ones which have reached
  the postage free amount.

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['view/res_partner_view.xml',
          'view/purchase_order_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
