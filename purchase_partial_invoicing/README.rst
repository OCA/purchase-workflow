Purchase partial invoicing
==========================

This module allows to partially invoice purchase order lines.
The 'Create invoices' from PO lines wizard allows to specify,
for each line, the quantity to invoice.

Installation
============

To install this module, you need to:

* Click on install button

This module depends on base_suspend_security module which can be found on apps.odoo.com or on the OCA/server-tools github repository.

Usage
=====

To use this module, you need to:

* In order to create invoice from purchase order line, you have to set invoice
  method on purchase order to "based on purchase order line".

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* The possibility to define quantities to not invoice on the purchase order
  line is not considered in the picking.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20purchase_partial_invoicing%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Adrien Peiffer <adrien.peiffer@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
