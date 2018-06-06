.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Procurement Purchase Group by Analytic
======================================

This module groups purchase order created from procurement by analytic account.
The analytic account used comes from project set on sale order.
On purchase order line, set this analytic account.

Installation
============

To install this module, you need to:

* Click on install button

Usage
=====

Example of use:

Create a sale order with an analytic account, set some products with route buy.
Run procurement, products are in the same purchase order (according other
rules like partner).
Create a second sale order, with another analytic account and set some products
with route buy.
Run procurement, 

Current behavior (without this module): add products in existing
purchase order.

Expected behaviour (with this module): get a separate purchase order for
these products (because it is not the same analytic account).

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20procurement_purchase_groupby_analytic%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Denis Roussel <denis.roussel@acsone.eu>

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
