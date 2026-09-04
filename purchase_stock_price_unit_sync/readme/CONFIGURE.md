The correction through the vendor bill needs `product_cost_price_avco_sync`
installed: it is that module which replays the valuation chain once the layer
changes, re-pricing what already left stock and correcting a valuation asked
for a date before the correction. Without it the bill keeps Odoo's standard
behaviour.

It applies to products with the **Average Cost (AVCO)** costing method and
**manual** inventory valuation. Refunds are left to Odoo, which compensates them
against the original bill with a logic of its own, and so is automated
valuation, where the journal entry of the layer is already posted and restating
it would pull stock valuation and accounting apart.
