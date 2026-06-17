To use this module:

1. Create or edit a purchase order.
2. Add a purchase order line with a Unit-based UoM, such as Units or a box UoM.
3. Enter a fractional quantity.

The quantity is proposed rounded UP to the next whole number.

The behavior is intentionally limited to the purchase order form onchange.
Imports, RPC calls, and custom code writes are not forced rounded.
