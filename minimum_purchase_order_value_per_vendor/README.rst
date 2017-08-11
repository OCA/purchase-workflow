.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License LGPL-3

=======================================
Minimum Purchase Order Value per Vendor
=======================================

This module allows you to to establish and automate a specific Purchase Order
Block Reason in the system: the "Minimum Purchase Order Value per Vendor".

This module depends on Purchase Order Block. You can find this module in:
https://github.com/OCA/purchase-workflow/purchase_order_block


Configuration
=============

* Go to ‘Purchases / Vendors’
* Click on a Vendor and inside the ‘Sales & Purchases’ page specify the
  non-required field ‘Minimum Purchase Amount’.
* Assign the security group “Release blocked RFQ” to users that should be able
  to release the block.


Usage
=====

Set the purchase block
----------------------
# Go to ‘Purchases / Purchase / Requests for Quotation’
# Create a new RFQ and you will see that by default the blocking reason
  ‘Minimum Purchase Order Value per Vendor’ is assigned to the field ‘Blocking
  reason’. Upon save, the blocking is not editable anymore, and a notification
  has been logged into the chatter, indicating ‘Order blocked with reason
  Minimum Purchase Order Value per Vendor’, so that all followers can receive
  it.

Search existing RFQ
-------------------
There is a filter ‘Blocked’ to search for orders that are blocked.
It is also possible to search RFQ’s with the Blocking reason ‘Minimum Purchase
Order Value per Vendor’.

Release the purchase block
--------------------------
# All the RFQ’s with a total amount surpassing the specified minimum purchase
  order value for that vendor (excluding taxes) will be automatically released
  and a notification will be sent to all the followers of that RFQ with a
  message ‘Order with block Minimum Purchase Order Value per Vendor has now
  been released’.
# If a blocked RFQ without surpassing the minimum value wants to be released, a
  user member of the security group “Release blocked RFQ” will see a button
  “Release block”. When pressing it a notification will be sent to all the
  followers as well.
# From this point and on, anyone seeing that RFQ will be able to validate it.

Validate the RFQ
----------------
# Press the button “Validate”. If there’s a block, and you do not have
  permissions, you will get an error message indicating that the RFQ is blocked
  because the total amount is below the vendor’s minimum value. You will need
  to wait until the minimum quantity is surpassed or request for it to be
  released by an authorized user.


Technical notes
===============
A Block Reason ‘Minimum Purchase Order Value per Vendor’ is created in the
Purchase Order Block during install.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Roser Garcia <roser.garcia@eficent.com>


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
