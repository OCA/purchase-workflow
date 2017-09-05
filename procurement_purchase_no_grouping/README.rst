.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================================
No grouping on procurement purchases
====================================

This module allows to not group generated purchase orders from procurements.
The grouping behaviour can be configurable at product category level.

Configuration
=============

Go to each product category, and select one of these values in the field
"Procured purchase grouping":

* *Standard grouping (default)*: With this option, procurements will generate
  purchase orders as always, grouping lines and orders when possible.
* *No line grouping*: With this value, if there are any open purchase order
  for the same supplier, it will be reused, but lines won't be merged.
* *No order grouping*: This option will prevent any kind of grouping.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Sergio Teruel <sergio.teruel@tecnativa.com>

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
