This module notifies to the employees following a the purchase order
when the associated products have been received into stock.

This module creates a new message subtype specifically created for those
notifications. This subtype is internal activated by default when subscribing.
The old purchase orders will be updated to assign this new subtype to the
existing followers, as long as they are still active employees.
