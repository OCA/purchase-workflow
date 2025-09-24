For users of the `Purchase hide prices` group, the unit price of purchase order
lines can't be edited, even for vendors whose prices are not hidden.

This is intentional: the `price_unit` field is removed from the view with
`groups`, so its value is never sent to the browser. Hiding it per line with
`invisible` would keep it editable, but the value would still be readable
with browser developer tools.

When a purchase order is sent by email:

- the attached PDF is rendered with the sender's rights: if the sender belongs
  to the `Purchase hide prices` group, the vendor receives a document without
  prices.
- the standard email body shows the order total amount, which is not hidden.
