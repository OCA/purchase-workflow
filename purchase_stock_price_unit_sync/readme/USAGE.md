There are two moments where the real price of a purchase shows up after the
goods have already been received, and both are synced:

- **The purchase order line.** Changing its price writes the new one on the
  stock moves that are already done and on their valuation layers.
- **The vendor bill.** Posting it at a different price applies that price to the
  whole receipt layer, instead of only to the part that has not left stock yet,
  which is what Odoo does on its own.

Correcting the same price in both places does not count it twice: whichever runs
second finds the layer already worth what it says and does nothing.

With `product_cost_price_avco_sync` installed, either of them replays the
valuation chain, so the outgoing moves valued in between are re-priced and a
stock valuation asked for a date before the correction comes out right. Without
it, only the layers themselves are written and the vendor bill keeps Odoo's
standard behaviour.
