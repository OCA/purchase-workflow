==================================
Discounts in product supplier info
==================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fpurchase_compute_order-lightgray.png?logo=github
    :target: https://github.com/druidoo/FoodCoops/tree/12.0


|badge1| |badge2| |badge3|

    This module helps you to decide what you have to buy.


**Table of contents**


.. contents::
   :local:


Usage
=====

**Provide tools to help a purchaser during the purchase process.**

    * Go to **Purchase > Purchase > Computed Purchase Order**, Create a new Compute Purchase Order (CPO)
    * Select a Supplier
    * Check the boxes to tell if you want to take into account the virtual stock or the draft sales/purchases.
    * Use the button 'Get products and stocks' to import the list of products you can purchase to this supplier (ie: products that have a product_supplierinfo for this partner). It especially calculates for each product:
        * the quantity you have or will have;
        * the average_consumption, based on the stock moves created during last 365 days;
        * the theoretical duration of the stock, based on the precedent figures.

    * Unlink the products you don't want to buy anymore to this supplier (this only deletes the product_supplierinfo)
    *  Add new products you want to buy and link them (this creates a product_supplierinfo)
    * Modify any information about the products: supplier product_code, supplier product_name, purchase price, package quantity, purchase UoM.
    * Modify the calculated consumption if you think you'll sell more or less in the future.
    * Add a manual stock quantity (positive if you will receive products that are not registered at all in Odoo, negative if you have not registered sales)
    * Click the "Update Products" button to register the changes you've made into the product supplierinfo.
    * Check the Purchase Target. It's defined on the Partner form, but you still can change it on each CPO.
    * Click the button 'Compute Purchase Quantities' to calculate the quantities you should purchase. It will compute a purchase order fitting the purchase objective you set, trying to optimize the stock duration of all products.
    * Click the "Make Purchase Order" button to convert the calculation into a real purchase order.


Possible Improvements:
    * offer more options to calculate the average consumption;

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/druidoo/FoodCoops/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/druidoo/FoodCoops/issues/new?body=module:%20purchase_compute_order%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
