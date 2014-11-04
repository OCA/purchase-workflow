Purchase Delivery Address
============================

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

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
