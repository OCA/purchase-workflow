.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Purchase Order Type
===================

Adds a configurable *type* on the purchase orders, allowing to predefine
some purchase order fields attached to this type.

This type can be used in filters and groupbys.

Configuration
=============

To configure this module, you need to:

#. Go to **Purchases > Configuration > Purchase types**
#. Modify / create the purchase order types
#. Assign (optionally) a default incoterm for this type.
#. Assign (optionally) a default picking type for this type (only incoming
   types).

You can also predefine a purchase order type in the partner:

#. Open a partner in **Purchases > Purchase > Vendors**.
#. Go to the **Sales & Purchases** page.
#. Select one type on the field.

Usage
=====

To use this module, you need to:

* Attribute a type when editing purchase orders
* Order Type will be autofilled when selecting a partner that has a type set
  in its data.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Known issues / Roadmap
======================

* Suggestion: add a default configuration attached to the types

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>

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
