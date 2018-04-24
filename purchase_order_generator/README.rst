.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Purchase Order Generator
========================

This module allows the user to configure the reception of products over a
certain period of time.

It features the configuration part and also a wizard that creates the purchase
order lines based on the configurator.

The user would be able enter the following information:

> * Product
> * Quantity Ratio
> * Sequence

Screenshots
===========

Create a configuration model, for instance a laying cycle:

.. image:: /purchase_order_generator/static/description/configuration_model.png
    :alt: Configuration model

You can access the wizard either by the menu, either when receiving products.
For example, when receiving 12,000 laying hens:

.. image:: /purchase_order_generator/static/description/transfer.png
    :alt: Transfer

.. image:: /purchase_order_generator/static/description/wizard.png
    :alt: Wizard

The purchase order automatically generated:

.. image:: /purchase_order_generator/static/description/result_po_generated.png
    :alt: Result

Installation
============

To install this module, you just need to select the module and make sure
dependencies are available.

Configuration
=============

No particular configuration to use this module.

Usage
=====

To use this module, you need to:

- Go on the configurator interface
- Define the interval of time in which you would like to receive your products
(ex: each week)
- Choose the products and the quantities for each element of the sequence

To generate purchase order lines thanks to the configurator you created:

- Use the wizard
- Choose the model you just created
- Define a starting date, a partner, a destination location and an initial
quantity
- Validate to generate the purchase order lines

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* this module will be complemented by a purchase_order_line_revision module

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20purchase_order_generator%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


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
