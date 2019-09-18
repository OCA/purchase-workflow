
Create a product of type consumable or product with:

* a value in field 'weight';
* set True on field 'compute_price_on_weight';
* add a Seller with a price.

Then create a purchase order with the product created, unit price will be
computed with: 'seller price' * 'product weight'.

A computed field 'total weight' is shown in purchase order line.

In this way, all other logic remains untouched, but the user can have a simple
solution to manage product with price on weight but with a different unit of
measure on warehouse (m, m2, etc.)
