This module overrides the `product.supplierinfo` model.
It splits the delay into two new delay fields, `Supplier Lead Time` and `Transport Lead Time`, to sum them into the actual `Lead Time`.
This allow users to get the information about the transportation lead time in order to plan the transport properly when relevant.
