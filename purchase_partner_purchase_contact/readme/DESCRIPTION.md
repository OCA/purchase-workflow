This module adds a **Purchase Contact** field to requests for quotation
and purchase orders.

**Key concept — not another address field**

Odoo already exposes the vendor and its addresses on the purchase order.
This module addresses a *different need*: tracking a named **contact
person** (e.g. procurement manager, account manager) who is the
day-to-day point of contact for the order, distinct from the vendor
company itself.

The purchase contact field allows you to:

- Select a specific contact person for a purchase order or request for
  quotation.

The contact must be a child contact (person) of the selected vendor.

When sending an RFQ or purchase order email, this contact is used as the
default recipient instead of the vendor company (falling back to the
vendor when no contact is set or it has no email address).
