This module adds a wizard to merge purchase order.


A wizard that can be called from tree view of purchase orders.
If merge criteria are validate:
All lines of all PO are "transferred" to the first one and some information like 'origin' and 'partner_ref' are concatenated.
We post a message on the chatter to indicate when the merge operation occurs and what were the PO concerned.
The empty PO are "canceled"

Merge criteria:
* PO are from the same supplier
* PO are in state 'draft'
* PO have the same
#. currency
#. picking type
#. incoterms
#. payment terms
#. fiscal position
