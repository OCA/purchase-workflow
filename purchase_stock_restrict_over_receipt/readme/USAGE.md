Validate a receipt of a purchase order as usual. The validation is refused,
and nothing is received, when:

- the received quantity of an order line would exceed its ordered quantity,
  counting the earlier receipts and returns of the line, or
- the receipt has a product that is not on the purchase order.

To receive the excess, update the purchase order first: raise the ordered
quantity of the line, or add a line for the product. The demand of the open
receipt follows the order. A line that was added by hand on the receipt is
kept next to it, and has to be removed before validating.

Returns to the vendor and receipts without a purchase order are not
restricted.
