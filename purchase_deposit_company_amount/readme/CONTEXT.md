When a purchase order is in a foreign currency, the deposit is usually
settled for an exact company currency amount that does not match the
exchange rate configured for that day. Odoo books the deposit at the rate,
so the deposit account never closes out cleanly against what was paid.

A paid deposit is a non-monetary asset, so the goods are measured at the
deposit's own rate for the prepaid portion and at the current rate for the
remainder. The difference is part of the acquisition cost rather than an
exchange gain or loss, which is why it is booked into the product lines.
