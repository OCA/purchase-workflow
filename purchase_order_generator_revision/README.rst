.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Purchase Order Generator Revision
=================================

This module was written to be able to create a wizard that will be able to
review the purchase order lines based on a pre-configured model found in the
module purchase_order_generator

The user would be able enter the following information:

* Order
* Model configured in the system
* Target
* Quantity received
* Effective date
* Revision factor
* New target
* Reason for the revision


Installation
============

To install this module, you need to:

* Make sure all the dependencies are available

Configuration
=============

No particular configuration to use this module

Usage
=====

To use this module, you need to:

- Place an order
- Receive it
- Enter the values in the wizard,
- Once Validated, the wizard will generate purchase order lines for the
  product that is derived from the product received or depends on it
- If needed the module allows a revision factor to be applied which will modify
  the remaining purchase order lines derived for the product received

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20purchase_order_generator_revision%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Adriana Ierfino <adriana.ierfino@savoirfairelinux.com>
* Bruno Joliveau <bruno.joliveau@savoirfairelinux.com>
* Agathe Mollé <agathe.molle@savoirfairelinux.com>

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
