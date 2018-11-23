.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License AGPL-3

===========================
Discount in purchase orders
===========================

This module allows to define a discount per line in the purchase orders. This
discount can be also negative, interpreting it as an increment.

It also modifies the purchase order report to include the discount field in it.

This module allows to input a discount in the supplier info form, and propagate
it to purchase order lines:

* The discount appears explicitly in purchase orders instead of being directly
  discounted in price.
* You can set prices and discounts on the same screen.

.. image:: /purchase_discount/static/description/product_supplierinfo_form.png


* A new field default_supplierinfo_discount is added on res.partner model.
  This value will be used as the default one, on each supplierinfo of that
  supplier.

.. image:: /purchase_discount/static/description/res_partner_company_form.png


Note: this setting is a new 'company' setting, unavailable for related
partners, as accounting-related Settings.

.. image:: /purchase_discount/static/description/res_partner_individual_form.png

Usage
=====

Go to **Purchase > Products**, open one product, and edit or add a record on
the **Vendors** section of the **Purchase** tab. You will see in the prices
section in the down part a new column called **Discount (%)**. You can enter
here the desired discount for that quantity.

When you make a purchase order for that supplier and that product, discount
will be put automatically.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/12.0

Known issues / Roadmap
======================

With this module, the *price_unit* field of purchase order line stores the gross price instead of the net price, which is a change in the meaning of this field. So this module breaks all the other modules that use the *price_unit* field with it's native meaning.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* OpenERP S.A.
* Ignacio Ibeas <ignacio@acysos.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Stefan Rijnhart <stefan@opener.amsterdam>
* `Tecnativa <https://www.tecnativa.com>`_:

  * Pedro M. Baeza
  * Vicent Cubells <vicent.cubells@tecnativa.com>

* Sudhir Arya <sudhir@erpharbor.com>

Icon
----

* Original Odoo purchase module icon
* https://openclipart.org/detail/159937/clothing-label-with-rope

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
