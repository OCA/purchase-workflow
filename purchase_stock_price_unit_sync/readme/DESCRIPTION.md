This module allows to sync picking cost prices with purchase order line
price when moves are already done.

It does the same when the price is corrected on the **vendor bill**. Odoo
corrects a price difference with a child valuation layer worth the difference
times the quantity that has not left stock yet, and sends the rest to the
expense account, so the moves that already left keep the cost that turned out
to be wrong. Here the invoiced price is applied to the whole receipt instead,
which leaves the bill on the same footing as changing the price on the purchase
order.

Can be used with product_cost_price_avco_sync.
