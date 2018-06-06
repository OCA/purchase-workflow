Example of use:

Create a sale order with an analytic account, set some products with route buy.
Run procurement, products are in the same purchase order (according other
rules like partner).
Create a second sale order, with another analytic account and set some products
with route buy.
Run procurement,

Current behavior (without this module): add products in existing
purchase order.

Expected behaviour (with this module): get a separate purchase order for
these products (because it is not the same analytic account).

For further information, please visit:

* https://www.odoo.com/forum/help-1
