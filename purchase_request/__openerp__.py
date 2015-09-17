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
    "name": "Purchase Request",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Purchase Management",
    "depends": ["purchase", "product"],
    "description": """
Purchase Request
================
You use this module if you wish to give notification of requirements of
materials and/or external services and keep track of such requirements.

Requests can be created either directly or indirectly. "Directly" means that
someone from the requesting department enters a purchase request manually.

The person creating the requisition determines what and how much to order,
and the requested date.

"Indirectly" means that the purchase request initiated by the application
automatically, for example, from procurement orders.

A purchase request is an instruction to Purchasing to procure a certain
quantity of materials services, so that they are is available at a
certain point in time.

A line of a requisition contains the quantity and requested date of the
material to be supplied or the quantity of the service to be performed. You
can indicate the service specifications if needed.


Installation
============

No specific instructions required.


Configuration
=============

No specific instructions requied.

Usage
=====
Purchase requests are accessible though a new menu entry 'Purchase
Requests', and also from the 'Purchase' menu.

Users can access to the list of Purchase Requests or Purchase Request Lines.

It is possible to filter requests by it's approval status.


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
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "views/purchase_request_view.xml",
    ],
    'demo_xml': [
        "demo/purchase_request_demo.xml",
    ],
    'test': [
        "test/purchase_request_users.yml",
        "test/purchase_request_data.yml",
        "test/purchase_request_status.yml"
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}