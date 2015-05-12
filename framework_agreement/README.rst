Long Term Agreement (or Framework Agreement) for purchases
==========================================================

With an agreement, a price is agreed between you and a supplier for a product,
under certain conditions.

An agreement portfolio groups together many agreements belonging to the same
supplier.

In a purchase order, the user can choose a portfolio. In that case, they will
be able to choose an agreement in the pricelist field.

Version 3.0 of this module changes the overall structure: the agreement is
not a special object anymore, but it is a special type of pricelist, with the
following features:

- It belongs to a portfolio (that is what identifies the pricelist as an
  agreement).
- It holds some information like incoterms and location, that is propagated to
  the order. In a way, the agreement works like a template for purchase orders.
- It has a button "Open Prices" to enter prices for every product and quantity
  using the same structure found in the supplier-specific prices in core Odoo.

In order for that to work, Pricelist Items have a new checkbox to use the
prices specific to the agreement.

Configuration
=============

To create a working setup with agreement portfolios, many objects need to be
created:

1. A portfolio, with information on the supplier and dates of validity.
2. Portfolio lines, with information on products and quantities.
3. Agreements, with delivery information
4. Supplier information objects, the link from products, suppliers and prices
  found in standard odoo
5. Price information lines, the lines in the former where prices are entered
6. Pricelist versions
7. Pricelist rules

Since this setup is complex, this module provides facilities to make setup
easier.

Once a portfolio is created, with one line per concerned product, the user
clicks the button "Create a new agreement", and objects 3-7 in the list above
are created automatically with the correct settings. At this point the
delivery information (like incoterms and locations) can be changed manually
in the agreement, and a convenient "open prices" button allows to actually set
the prices agreed upon.

When the agreement is selected in a Purchase Order, the delivery information is
propagate, and apart from that, it works in a similar fashion to a standard
pricelist for determining the prices for each product.

Credits
=======

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Yannick Vaucher <yannick vaucher@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>

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
