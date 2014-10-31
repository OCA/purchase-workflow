Purchase Delivery Address
============================

This module adds a delivery address to the purchase order, which is
automatically propagated to the generated picking.

Moreover, when a sale order generates a purchase in drop shipping mode, the
generated purchase has the delivery address set.

The idea is that this way dropshipping pickings have a trace of the desired
delivery address. The partner_id field of the picking is already used for the
supplier.


Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
