This module adds a new "Based on" option to pricelist rules: **Last Purchase
Price**. The base price of the rule is the unit price, net of discount, of
the most recent confirmed purchase order line of the product. It is converted
to the unit of measure and the currency being priced.

Only purchases of the pricelist's company are considered, or of the current
company when the pricelist is shared between companies, so a purchase made by
another company never sets the price.

Products that were never purchased fall back to their cost.
