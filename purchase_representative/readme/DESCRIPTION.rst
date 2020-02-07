This module adds the field *Purchase Representative* to Purchase
Orders. This field is present in Standard Odoo v12. The user specified will
be the contact person for the purchase order.

Additionally, it defaults it to the user doing a procurement to overcome the
known flaw of Odoo (until v13) which changes the user in the transaction when
using `sudo`.
