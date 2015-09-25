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
    "name": "Purchase Request to Bid",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Purchase Management",
    "depends": ["purchase_request", "purchase_requisition"],
    "description": """
Purchase Request to Bid
=======================
This module introduces the following features:
* The possibility to create new Bids or update existing Bids from Purchase
Request Lines.
* The possibility to create Purchase Requests on the basis of Procurement
Orders.

Installation
============

No specific instructions required.


Configuration
=============

No specific instructions requied.

Usage
=====
Create Purchase Requests from Procurement Orders
------------------------------------------------
Go to the product form, in tab 'Procurement' and choose 'Purchase Request'.
When a procurement order is created and the supply method is 'Make to Order'
the application will now create a Purchase Request.


Create Bids from Purchase Requests
----------------------------------
Go to the Purchase Request Lines from the menu entry 'Purchase Requests',
and also from the 'Purchase' menu.

Select the lines that you wish to initiate the RFQ for, then go to 'More'
and press 'Create Purchase Bid'.

You can choose to select an existing Draft Bid or create a new one.

In case that you chose to select an existing Bid, the application will search
for existing lines matching the request line, and will add the extra
quantity to them.

In case that you create a new RFQ, the request lines will also be
consolidated into as few as possible lines in the RFQ.


For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

Procurement Orders will no longer create Purchase Requisitions. The flag
'Purchase requisition' in the product form now becomes invisible.



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
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
        "views/product_view.xml",
        "views/procurement_view.xml",
    ],
    'demo_xml': [],
    'test': [
        "test/purchase_request_from_procurement.yml",
        'test/purchase_request_users.yml',
        'test/purchase_request_data.yml',
        'test/purchase_request.yml',
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}