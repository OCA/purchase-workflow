.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Discounts in product supplier info
==================================

This module allows to input a discount in the supplier info form, and propagate
it to purchase order lines:

* The discount appears explicitly in purchase orders instead of being directly
discounted in price.
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
* Jonathan Nemry <jonathan.nemry@acsone.eu>

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
