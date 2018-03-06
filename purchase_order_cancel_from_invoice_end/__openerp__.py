# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
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
    "name": "Add transition invoice_end to cancel in the workflow",
    "version": "1.0",
    "author": "Eficent",
    "category": "Generic Modules/Account",
    "description": """
This module was written to extend the purchasing capabilities of Odoo.
If the state of the PO is 'approved', there is no transition foreseen in
order to cancel the PO.

The user might be blocked in the following situation:
- Create a purchase order with invoicing set as Based on incoming shipment
- Validate the purchase order, create the shipment
- Then, cancel it (the shipment)
- Return back in the purchase order, the PO should be in shipping exception
- Hit the "manually corrected"
- Then, try to cancel the PO: nothing happens.



Known issues / Roadmap
======================

This module only applies to verion 7.0. In version 8.0 the limitation was
resolved by the following commit:
https://github.com/odoo/odoo/commit/4a281754db610d004701ce8edd9aeed32e766af4


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
    "website": "http://www.eficent.com/",
    "license": "",
    "depends": [
        "purchase"
    ],
    "demo": [
        'purchase_order_demo.yml'
    ],
    "data": [
        "purchase_workflow.xml"
    ],
    "test": [
        "test/cancel_order_1.yml",
        "test/cancel_order_2.yml"
    ],
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
