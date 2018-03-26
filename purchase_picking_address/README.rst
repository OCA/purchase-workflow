.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

========================
Purchase Picking address
========================

This module allows to add a delivery address on picking types, so the purchase
order is more accurate.


Configuration
=============

#. Go to ’Inventory / Configuration / Settings’
#. Select the option ’Storage Locations’
#. Go to ‘Inventory / Warehouse Management / Operation Types’
#. Create a new operation type with code type vendors and select a 'Purchase
   delivery address'

Usage
=====

#. Go to 'Purchases / Requests for Quotation'
#. Create a Purchase order and select the created operation type
#. The delivery address of the purchase will be the one selected on the
   operation type


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Enric Tobella <etobella@creublanca.es>.

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
