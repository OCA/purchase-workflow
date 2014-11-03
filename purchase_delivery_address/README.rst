Purchase Delivery Address
============================

This module adds a delivery address to the purchase order, which is
automatically propagated to a corresponding field in the generated picking.

Some of this logic was present in the core, but is not functioning properly.
In any case, this module makes the existing field in the purchase order
visible, adding some functionality and tests. The destination address on the
Picking is new.

Moreover, when a sale order generates a purchase in drop shipping mode, the
generated purchase has the delivery address set.

The idea is that this way dropshipping pickings have a trace of the desired
delivery address. The partner_id field of the picking is already used for the
supplier.


Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
