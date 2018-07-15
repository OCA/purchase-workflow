.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================================
Purchase Supplier Rounding Method - Triple Discount
===================================================

This module is a glue module to make compatible the modules
```purchase_supplier_rounding_method``` and
```account_invoice_triple_discount``` and is automatically installed if both
modules are installed.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Known issues / Roadmap
======================

* For inheritance reasons, the following function will be overwritten,
  removing the call of super.

1. ```purchase.order.line```: ```_calc_line_base_price()```
2. ```account.nvoice.line```: ```_compute_price()```

Credits
=======

Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>

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
