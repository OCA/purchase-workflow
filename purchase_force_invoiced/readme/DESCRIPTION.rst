This module adds the possibility for users to force the invoice status of the
purchase orders to 'No Bill to Receive', even when not all the
quantities, ordered or delivered, have been invoiced.

This feature is useful in the following scenario:

* The supplier disputes the quantities to be billed for, after the
  products have been delivered to her/him, and you agree to reduce the
  quantity to invoice (without expecting a refund).

* When migrating from a previous Odoo version, in some cases there is less
  quantity billed to what was delivered, and you don't want these old purchase
  orders to appear in your 'Waiting Bills' list.
