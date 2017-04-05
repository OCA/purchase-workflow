.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Purchase Supplier Rounding Method
=================================

This module extend account module, to add new rounding method used by some
suppliers. The new rounding method is used for purchase orders and In invoices.

Use Case
--------

Some of suppliers compute invoice line subtotal differently than Odoo.

In Odoo, by default:

``` price_subtotal = round(unit_price * (1 - discount / 100) * qty)```

  .. figure:: /purchase_supplier_rounding_method/static/description/subtotal_normal.png
     :width: 800 px

For some suppliers:

``` price_subtotal = round(round(unit_price * (1 - discount / 100)) * qty)```

  .. figure:: /purchase_supplier_rounding_method/static/description/subtotal_round_net_price.png
     :width: 800 px

This module manage this second case to generate supplier invoices with the
same value.

Configuration
-------------

* Add a new field 'rounding_method' on a partner with two keys:
    * 'normal': classical computation method, by default.
    * 'round_net_price': round a firt time the net price, and then round again.

  .. figure:: /purchase_supplier_rounding_method/static/description/partner_setting.png
     :width: 800 px

Credits
=======

Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>
