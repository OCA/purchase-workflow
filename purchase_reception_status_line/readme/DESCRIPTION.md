This module adds a field *Reception Status* on purchase orders line. On
a confirmed purchase order line, it can have 3 different values:

- Nothing Received
- Partially Received
- Fully Received

Also takes this into account when computing the reception status for the
purchase order.

**Highly Recommended:** Install the `purchase_order_line_menu` module to access
the reception status field in the purchase order line tree view for better
visibility and management.
