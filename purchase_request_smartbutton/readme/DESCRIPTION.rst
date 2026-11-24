``purchase_request`` puts a smart button on the request pointing at the
purchase orders it produced. Nothing goes the other way: from an RFQ, or from
the vendor bill that followed it, there is no way back to what was originally
asked for and by whom.

This module adds that return path, as a smart button on the purchase order
and on the vendor bill.

On a bill the requests are collected through every purchase order line the
bill was built from, so a bill consolidating several orders reaches the
requests of all of them.
