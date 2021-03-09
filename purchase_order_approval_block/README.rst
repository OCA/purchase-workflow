.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License LGPL-3

=============================
Purchase Order Approval Block
=============================

This module allows you to block the approval of an RFQ when an Approval
Block Reason has been provided. Upon confirmation of an RFQ the orders will be
waiting for approval by a Manager.

Configuration
=============

* Go to ‘Purchases / Configuration / Purchase Approval Block Reasons’ and create
  the blocking reasons as needed, providing a name and a description. A field
  ‘Active’ allows you to deactivate the reason if you do not plan to use it
  any more.
* Assign the security group 'Release blocked RFQ' to users that should be able
  to release the block. Users in group 'Purchase / Managers' are by default
  assigned to this group.

Usage
=====

Set the Purchase Approval Block
-------------------------------

#. Go to ‘Purchases / Purchase / Requests for Quotation’
#. Create a new RFQ and indicate the approval block reason (found in the
   right hand side of the screen, below the order date).

Search existing RFQ
-------------------

There is a filter ‘Blocked’ to search for orders that are blocked for approval.
It is also possible to search RFQ’s with a specific block reason.

Confirm the RFQ
---------------

#. Press the button ‘Confirm’. If there’s an approval block, the order will
   be set to status 'To Approve'. You will then need to request a Purchase
   Manager to approve it.

Release the purchase approval block
-----------------------------------

While the RFQ is in draft, members of security group ‘Release blocked RFQ’,
can see a button ‘Release Approval Block’. From this point and on, anyone
seeing that RFQ will be able to validate it.

Notifications to followers
--------------------------

Followers of the RFQ receive notifications when an approval block has been
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
