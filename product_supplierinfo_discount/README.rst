.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==================================
Discounts in product supplier info
==================================

This module allows to input a discount in the supplier info form, and propagate
it to purchase order lines:

* The discount appears explicitly in purchase orders instead of being directly
  discounted in price.
* You can set prices and discounts on the same screen.

.. image:: /product_supplierinfo_discount/static/description/product_supplierinfo_form.png


* A new field default_supplierinfo_discount is added on res.partner model.
  This value will be used as the default one, on each supplierinfo of that
  supplier.

.. image:: /product_supplierinfo_discount/static/description/res_partner_company_form.png


Note: this setting is a new 'company' setting, unavailable for related partners,
as accounting-related Settings.

.. image:: /product_supplierinfo_discount/static/description/res_partner_individual_form.png

Installation
============

This module requires *purchase_discount* module, that it's also available in
this repository.

Configuration
=============

To see prices and discounts on supplier info view, you have to enable the
option "Manage pricelist per supplier" inside *Configuration > Purchases*

Usage
=====

Go to Purchase > Products, open one product, and edit or add a record on the
*Suppliers* section of the *Procurements*. You will see in the prices section
in the down part a new column called *Discount (%)*. You can enter here
the desired discount for that quantity.

When you make a purchase order for that supplier and that product, discount
will be put automatically.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/10.0

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Stefan Rijnhart <stefan@opener.amsterdam>

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
