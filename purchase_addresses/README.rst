Purchase Address Management
===========================

Description
===========

This module (together with stock_addresses and sale_addresses) manages in a
coherent way the following addresses in the standard Odoo workflows:

* origin address
* destination address
* consignee


delivery addresses management:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module adds a delivery address to the purchase order, which is
automatically propagated to a corresponding field in the generated picking.

Some of this logic was present in the core, but is not functioning properly.
More specifically, in the core, a dropshipping purchase order has two fields:
partner_id is used for the supplier, and dest_address_id contains the address
of the customer. This works, except that the address is not visible because of
odoo/odoo#2950).

On the other hand, the picking has only one field: the partner_id. By default,
it takes the delivery address of the PO if there is one, or else the supplier.
The stock.move also has a partner_id field that is filled with the same
partner.  To make things even more confusing, in v7 the partner_id of the move
is the supplier, while the partner_id of the picking is the customer address.

This means that in v8 with core modules, we do not clearly see the supplier and
the customer address of a picking. Those two fields are important to handle
dropshipping.

With this module, in dropshipping mode the generated picking will have the
supplier in the partner_id field, and the customer address in the new
delivery_address_id field.



Credits
=======

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
