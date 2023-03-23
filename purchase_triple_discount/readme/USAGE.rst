Create a new purchase order and add discounts in any of the three discount
fields given. They go in order of precedence so discount 2 will be calculated
over discount 1 and discount 3 over the result of discount 2. For example,
let's divide by two on every discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = 50% -> Amount = 150.00
  - Disc. 3 = 50% -> Amount = 75.00

You can also use negative values to charge instead of discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = -5% -> Amount = 315.00

* When the purchase order is validated, the discounts will be added to the
  corresponding vendor pricelist.
* Vendor pricelists can be edited as well with their corresponding new second
  and third discounts.
* A default second or third discount can be set in every vendor
  *Sale & Purchases* tab.
