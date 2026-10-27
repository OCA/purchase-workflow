On a purchase order, the operation type follows the partner and the
incoterm: the warehouse's Transit receipt type when the incoterm is
flagged *Transit Receipt*, its usual receipt type otherwise. It can
still be changed by hand, until the partner or the incoterm changes.

Validate the Transit receipt when the vendor ships the goods; the usual
reception is then ready in the warehouse.

Other modules can extend `purchase.order._requires_transit_receipt()`
to send more purchases through the Incoming transit.
