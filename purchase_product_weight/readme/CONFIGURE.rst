
Create a product of type consumable or product with:

* a value in field 'weight';
* set True on field 'compute_price_on_weight';
* add a Seller with a price.

Then create a purchase order with the product created, unit price will be
computed with: 'seller price' * 'product weight'.

As weight can variate, a computed field 'total weight' will be added to
purchase order line, and if this value is changed the unit price will be
re-computed on 'total weight' / 'product qty'.

In this way, all other logic remains untouched, but the user can have a simply
solution to manage product with price on weight but with a different u.m. on
warehouse (m., m2, etc.)
