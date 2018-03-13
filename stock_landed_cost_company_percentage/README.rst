.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Stock landed cost company percentage
====================================

This module allows you to add a fixed percentage of landed costs to every
received items.

Configuration
=============

* Go to Inventory > Master Data > Products
* Create landed cost product. Make sure the landed cost box is checked.
* Go to Settings > Company
* Select a company and go to the Accounting tab
* Select or create a journal for the landed costs accounting entries
* Add landed costs by selecting the landed cost product and entering the
  percentage

Usage
=====

* Go to Purchases > Purchase > Requests for Quotation
* Select or create a new one
* Confirm the order and receive the products
* Go to Inventory > Operations > Landed Costs
* A new landed cost has been created for the receipt you just processed.
  The value has been calculated based on the percentage and the total cost of
  the received products.

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

* Bhavesh Odedra <bodedra@opensourceintegrators.com>

Funders
-------

The development of this module has been financially supported by:

* Open Source Integrators <http://www.opensourceintegrators.com>

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
