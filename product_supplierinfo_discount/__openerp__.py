# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Discounts in product supplier info",
    "version": "1.0",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "description": """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Discounts in product supplier info
==================================

This module allows to put a discount in the supplier info form, and propagate
it to purchase orders, having two advantages over pricelists:

* The discount is directly put on purchase orders instead of reducing the
  unit price.
* You can set prices and discounts on the same screen.

Installation
============

This module requires *purchase_discount* module, that it's also available in
this repository.

Configuration
=============

To see prices and discounts on supplier info view, you have to enable the
option "Manage pricelist per supplier" inside *Configuration > Purchases*

Usage
=====

Go to Purchase > Products, open one product, and edit or add a record on the
*Suppliers* section of the *Procurements*. You will see in the prices section
in the down part a new column called *Discount (%)*. You can enter here
the desired discount for that quantity.

When you make a purchase order for that supplier and that product, discount
will be put automatically.

Known issues / Roadmap
======================

* The discount is always applied, independently if you have based
  your pricelist on other value than "Supplier Prices on the product form".

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

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
    "website": "www.serviciosbaeza.com",
    "license": "AGPL-3",
    "depends": [
        'product',
        'purchase_discount',
    ],
    "data": [
        'views/product_supplierinfo_view.xml',
    ],
    "installable": True,
}
