Purchase request lines are ordered by ``id desc``, so the last line typed
shows up first and the order cannot be changed. Every other document in Odoo
that has lines -- sale orders, purchase orders, invoices -- carries a
``sequence`` field with a drag handle instead.

This module brings purchase requests in line with that behaviour:

* a ``sequence`` field, with the usual drag handle in the list, so lines can
  be reordered and the order is kept;
* a ``#`` column showing the position of each line in the request.

The position is computed on the fly and is not stored: it is a reading aid,
not an identifier. Removing a line renumbers the ones below it.
