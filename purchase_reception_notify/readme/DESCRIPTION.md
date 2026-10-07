This module automatically notifies the employees following a purchase order
as soon as the associated products have been received into stock.

It also introduces a new message subtype specifically created for those
notifications. This subtype is set to internal by default when
subscribing. The old purchase orders will be updated to assign this new
subtype to the existing followers, as long as they are still active
employees.
