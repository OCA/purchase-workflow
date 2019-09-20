==================================
Discounts in product supplier info
==================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fpurchase_package_qty-lightgray.png?logo=github
    :target: https://github.com/druidoo/FoodCoops/tree/12.0

|badge1| |badge2| |badge3|

This module allows to input a Package quantity in the supplier info form, and propagate
it to purchase order lines:

* The package quantity appears in purchase orders lines.

**Table of contents**

.. contents::
   :local:

Installation
============

This module requires **purchase_discount** module.


Usage
=====

Go to **Purchase > Products**, open one product, and edit or add a record on
the **Vendors** section of the **Purchase** tab. You will see in the prices
section in the down part a new column called **Package Qty**. You can enter
here the seller's Package Quantity.

You can assign the Price Policy too. It's per UOM or per Package.

Based on Price policy the amount will be calculated.
    * If you choose per UOM then it will be the default calculation.
    * If you choose per Package then it will consider the quantity of **Number of Packages** column

**Package Qty** and **Number of Packages** columns will be forwarded to Incoming shipment when you confirm the PO.
Same way **Package Qty**, **Number of Packages** and **Price Policy** will be forwarded to Vendor bills when you Create an invoice from PO.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/druidoo/FoodCoops/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/druidoo/FoodCoops/issues/new?body=module:%20purchase_package_qty%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Druidoo
* Julien WESTE
* Sylvain LE GAL

Contributors
~~~~~~~~~~~~

* Druidoo <https://www.druidoo.io>
* Julien WESTE
* Sylvain LE GAL (https://twitter.com/legalsylvain)


Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/purchase-workflow <https://github.com/OCA/purchase-workflow/tree/11.0/product_supplierinfo_discount>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
