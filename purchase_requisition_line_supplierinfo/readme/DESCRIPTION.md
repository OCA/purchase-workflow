Adds a *Lead Time* and a *Minimum Quantity* to the lines of a blanket
order, and writes both onto the vendor pricelist line
(`product.supplierinfo`) that confirming the blanket order creates.

In standard Odoo, confirming a blanket order creates one vendor
pricelist line per agreement line carrying only the agreed price and
currency. Its lead time is the default of one day and its minimum
quantity the default of one unit, whatever was agreed with the vendor.
Purchase orders placed under the agreement, manually or by the
procurement scheduler, select that pricelist line and plan their
receipt for the next day.

With this module:

- the lead time and minimum quantity agreed with the vendor are set on
  each blanket order line and written onto the pricelist line it
  creates; changing them on a confirmed agreement updates that
  pricelist line too, the same way standard does for the price;
- a request for quotation opened from the blanket order (*New
  Quotation*) plans its lines on the agreement's lead time instead of
  today.

Closing or cancelling the agreement still removes the pricelist line,
as in standard.
