.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
No grouping on procurement purchases
====================================

This module allows to not group generated purchase orders from procurements.
The grouping behaviour can be configurable at product category level.

Configuration
=============

To configure this module, you need to:

go to each product category, and select one of these values in the field
*Procured purchase grouping*:

* *Standard grouping (default)*: With this option, procurements will generate
  purchase orders as always, grouping lines and orders when possible.
* *No line grouping*: With this value, if there are any open purchase order
  for the same supplier, it will be reused, but lines won't be merged.
* *No order grouping*: This option will prevent any kind of grouping.

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

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Alex Comba <alex.comba@agilebg.com>
* Daniel Rodriguez Lijo <drl.9319@gmail.com>

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
