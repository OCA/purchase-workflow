When a request for quotation (RFQ) is created from a purchase request with
`purchase_request`, each RFQ line keeps a link to the purchase request lines it
covers. That link is what lets the purchase request follow the purchase: it
shows the RFQ, moves to *Purchased* when the order is confirmed and tracks the
received quantities through allocations.

The standard *Create Alternative* action of `purchase_alternative` builds new
RFQs for other vendors by copying the product lines of the original RFQ, but
the copies lose the link to the purchase request. If an alternative RFQ ends
up being the one confirmed, the purchase request never learns about it.

This module propagates the purchase request lines and their allocations to the
lines of every alternative RFQ created with *Create Alternative*, so the
purchase request follows whichever RFQ wins the comparison.

It is installed automatically when both `purchase_request` and
`purchase_alternative` are installed.
