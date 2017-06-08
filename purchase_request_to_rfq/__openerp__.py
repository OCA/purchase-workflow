# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    "name": "Purchase Request to RFQ",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Purchase Management",
    "depends": ["purchase_request", "purchase", "purchase_group_hooks"],
    "description": """
Purchase Request to RFQ
=======================
This module adds the possibility to create or update Requests for
Quotation (RFQ) from Purchase Request Lines.

Installation
============

No specific instructions required.


Configuration
=============

No specific instructions requied.

Usage
=====
Go to the Purchase Request Lines from the menu entry 'Purchase Requests',
and also from the 'Purchase' menu.

Select the lines that you wish to initiate the RFQ for, then go to 'More'
and press 'Create RFQ'.

You can choose to select an existing RFQ or create a new one. In the later,
you have to choose a supplier.

In case that you chose to select an existing RFQ, the application will search
for existing lines matching the request line, and will add the extra
quantity to them, recalculating the minimum order quantity,
if it exists for the supplier of that RFQ.

In case that you create a new RFQ, the request lines will also be
consolidated into as few as possible lines in the RFQ.


For further information, please visit:

* https://www.odoo.com/forum/help-1


Known issues / Roadmap
======================

No issues have been identified


Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
    """,
    "init_xml": [],
    "update_xml": [
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_order_view.xml",
    ],
    'demo_xml': [],
    'test': [
        'test/purchase_request_users.yml',
        'test/purchase_request_data.yml',
        'test/purchase_request.yml',
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}