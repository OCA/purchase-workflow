.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License AGPL-3

===========================
Discount in purchase orders
===========================

This module allows to define a discount per line in the purchase orders. This
discount can be also negative, interpreting it as an increment.

It also modifies the purchase order report to include the discount field in it.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/11.0

Known issues / Roadmap
======================

With this module, the *price_unit* field of purchase order line stores the gross price instead of the net price, which is a change in the meaning of this field. So this module breaks all the other modules that use the *price_unit* field with it's native meaning.

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
* Pedro M. Baeza <pedro.baeza@tecnativa.com>

Icon
----

* Original Odoo purchase module icon
* https://openclipart.org/detail/159937/clothing-label-with-rope

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
