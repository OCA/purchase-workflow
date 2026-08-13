Odoo lets you put several RFQs in competition for the same need, as
*alternatives* of one another. ``purchase_request`` keeps, on every request
line, the purchase order lines that need ended up on, and derives the
purchased quantity from them.

The two do not know about each other: when an RFQ born from a purchase
request gains an alternative, the alternative carries no trace of the
request. Opening the alternative gives no way back to what was asked for,
and the request keeps reporting only the quantity of the original RFQ.

This module links the request lines to the alternatives as well, both when
an alternative is created from an existing RFQ and when an existing RFQ is
attached as an alternative.

Lines are paired by product. Linking a request line to alternative lines of
other products would inflate the quantity the request believes has been
purchased, so only matching products are connected.
