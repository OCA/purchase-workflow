.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License LGPL-3

=======================
Purchase Minimum Amount
=======================

This module allows you to establish and automate a specific Purchase Order
Approval Block Reason in the system: the 'Minimum Purchase Order Amount per
Vendor'.

Configuration
=============

* Go to 'Purchases / Purchase / Vendors'
* Click on a Vendor and inside the 'Sales & Purchases' page specify the
  non-required field 'Minimum Purchase Amount'.
* Assign the security group 'Release blocked RFQ' to users that should be able
  to release the block. Users in group 'Purchase / Managers' are by default
  assigned to this group.

Usage
=====

Set the Purchase Approval Block
-------------------------------

#. Go to 'Purchases / Purchase / Requests for Quotation'
#. Create a new RFQ and upon saving if the Untaxed Amount is below the
   Purchase Minimum Amount specified in that vendor, then the Approval Block
   Reason is automatically set and the Approval Block Reason is not editable
   anymore.

Search existing RFQ
-------------------

There is a filter 'Blocked' to search for orders that are blocked.
It is also possible to search RFQ’s with the Approval Block Reason 'Minimum
Purchase Order Amount per Vendor'.

Confirm the RFQ
---------------

#. Press the button ‘Confirm’. If there’s an approval block, the order will
   be set to status 'To Approve'. You will then need to request a Purchase
   Manager to approve it.

Release the purchase approval block
-----------------------------------

#. All the RFQ’s with a total amount surpassing the specified Minimum Purchase
   Order Amount for that vendor (excluding taxes) are automatically released.
#. If a blocked RFQ without surpassing the minimum amount wants to be
   released, a user member of the security group 'Release RFQ with approval
   block' can see a button 'Release Approval Block'. When pressing it, anyone
   seeing that RFQ is able to validate it.

Notifications to followers
--------------------------

#. Followers of the RFQ receive notifications when an approval block has been
   set or released.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Roser Garcia <roser.garcia@eficent.com>
* Darshan Patel <darshan.patel.serpentcs@gmail.com>

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
