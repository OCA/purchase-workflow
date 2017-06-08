============================
Purchase Internal Validation
============================

This module modifies the purchase workflow in order to validate
purchases that exceeds the amount set in the Purchase configuration panel.
It differs from the purchase_double_validation module by inserting the
validation step in the purchase order workflow before the confirmation,
not after.

Configuration
=============

* Set the limit in the Purchase configuration panel
  By default the limit amount is set to a very high value to prevent
  conflicts with unit tests in other modules.
* Add some users to the Purchase / Validator and Purchase / User groups
* Make sure those users have correct email addresses to receive notifications

Usage
=====

* As a Purchase user, go to Purchase > Purchases > Quotations
* Create a quotation exceeding the limit and try to confirm it
* As a Purchase validator, validate or refuse the quotation
* As the user, you can now confirm the PO

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* ..

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new>`_.


Credits
=======

Contributors
------------

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Vincent Vinet <vincent.vinet@savoirfairelinux.com>
* David Dufresne <david.dufresne@savoirfairelinux.com>

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
