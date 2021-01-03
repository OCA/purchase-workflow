Without this module, if you increase the quantity on a purchase line, the
increase is propagated on the reception, however nothing is done if the
quantity is decreased. This module changes the behavior of Odoo and propagates
the decrease if the new purchased quantity is below the already received
quantity. The increase is also propagated.

When used with `purchase_delivery_split_date` it allows to split a purchase line
when a vendor announces he can only make a partial delivery for date1 and the
remaining quantity at a later date.
