.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License AGPL-3

===========================
Discount in purchase orders
===========================

This module allows to define a discount per line in the purchase orders. This
discount can be also negative, interpreting it as an increment.

It also modifies the purchase order report to include the discount field in it.

Installation
============

You need an Odoo/OCB installation updated up to at least on 27 august of 2015,
containing revision `617ef49 <https://github.com/odoo/odoo/commit/617ef49959d027fab52e2be74aa4c0dc3ce60e30>`_

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/9.0

Known issues / Roadmap
======================

* Improvement made into 8.0: load price with discount in stock_move when confirm a purchase order
(https://github.com/OCA/purchase-workflow/commit/e5b578b9e7613c4535fa77768207e8c44acd4822)
* Issue into the previous 8.0 improvement: Purchase discount not taken into account in the purchase report
(https://github.com/OCA/purchase-workflow/issues/265)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* OpenERP S.A.
* Ignacio Ibeas <ignacio@acysos.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Icon
----

* Original Odoo purchase module icon
* https://openclipart.org/detail/159937/clothing-label-with-rope

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
