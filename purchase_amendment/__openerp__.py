# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier, Leonardo Pistone, Jordi Ballester
#    Copyright 2015 Camptocamp SA
#    Copyright 2015 Eficent
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
#


{
    "name": "Purchase Amendment",
    # description is in README.rst
    "version": "0.2",
    "depends": ["purchase",
                "stock_split_picking",
                "purchase_ignore_cancelled_po_lines"],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "description": """
Purchase Amendment
==================
This module is meant to assist the users in handling the cases when the company
changes his mind about a purchase.

See also `sale_amendment` (in https://github.com/OCA/sale-workflow)
which covers a similar use case for changes in sale orders.


Usage
=====
Once a purchase order is confirmed, an 'Amend' button is shown on the
view's header. Clicking on this button will open a new window with the
order's lines and the quantity to amend.

Amending a purchase order will cancel the stock moves and create new
ones with the new quantities.

An invoiced purchase order cannot be amended.

Known issues / Roadmap
======================

Credits
=======

Contributors
------------

* Joel Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
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
    "installable": True,
    "data": ["view/purchase_order.xml",
             "view/purchase_order_amendment_view.xml",
             "data/purchase_workflow.xml",
             ],
    "test": [],
}
