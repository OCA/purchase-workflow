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
    "name": "Purchase Order Cancel when PO is invoiced based on PO lines",
    "version": "1.0",
    "author": "Eficent",
    "category": "Generic Modules/Account", 
    "description": """
This module was written to extend the purchasing capabilities of Odoo,
and allows the user to cancel an approved purchase order where the invoice
control is based on PO lines.

Currently, when the user chooses the invoice control 'Based on Purchase
Order Lines', if she then presses the button 'Cancel' the
PO is not cancelled, but the purchase order lines are cancelled, leaving
the Purchase Order in an inconsistent state.

The system will continue to restrict the user from cancelling the
Purchase Order if:
* One of the associated Incoming Shipments has been completed
* One of the associated Purchase Order Lines has been invoiced, and the
invoice is not in state 'cancelled' or 'draft'.

Known issues / Roadmap
======================

This module only applies to verion 7.0. In version 8.0 the limitation is
resolved in the 'purchase' module.

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
    "demo": [], 
    "data": [
        "purchase_workflow.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}