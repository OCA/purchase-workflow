.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Purchase Order Approved
=======================

This module extends the functionality of purchases adding a new state
*Approved* in purchase orders before the *Purchase Order* state. Additionally
add the possibility to set back to draft a purchase order in all the states
previous to *Purchase Order*. From a user point of view, this change introduces
a two-step validation process of the purchase order.

In this new *Approved* state:

* You cannot modify the purchase order.
* However, you can go back to draft and pass through the workflow again.
* The incoming shipments are not created. You can create them by clicking the
  *Convert to Purchase Order* button, also moving to state *Purchase Order*.

The new state diagram is depicted below:

.. image:: purchase_order_approved/static/description/schema.png
   :width: 500 px
   :alt: New states diagram

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/10.0

Configuration
=============

This new workflow can be activated by company and by supplier.

To activate the new workflow by company:

#. Go to 'Purchases > Configuration > Settings'.
#. In the *Logistics* section in the *Configuration* tab you can set the *Use
   State 'Approved' in Purchase Orders*.

To activate the new workflow by supplier:

#. Open the supplier form view.
#. In the *Purchase* section in the *Sales & Purchases* tab the field
   *Purchase requires second approval* allows you to select the policy to
   apply for the current supplier. 'Never' | 'Always' | 'Based on company policy'


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>
* Laurent Mignon <laurent.mignon@acsone.eu>

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
