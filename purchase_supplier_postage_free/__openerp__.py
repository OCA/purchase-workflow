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
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Purchase Management',
 'depends': ['purchase',
             'web_context_tunnel',
             ],
 'description': """
Purchase Supplier Postage Free
==============================

Add a field "Postage free above amount" on the suppliers, which is an
optional amount above which the supplier does not charge the shipping
fees.

Display this amount on the purchase orders as an indication and add a filter on
the purchase orders showing the ones which have reached the postage free
amount.


Usage
=====

To use this module, you need to:

* Configure the postage free amount on the products suppliers
* Use the *Free Postage Reached* filter and look at the indicator on the
  purchase orders


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20purchase_supplier_postage_free%0Aversion:%207.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
 """,
 'website': 'http://www.camptocamp.com',
 'data': ['view/res_partner_view.xml',
          'view/purchase_order_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
