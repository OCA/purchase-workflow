This module extends ``purchase_receipt_expectation_manual`` by splitting
received purchase lines.

When the manual receipt wizard is confirmed, new purchase lines are generated
with the wizard lines; then, the new PO lines are used to create the stock
moves for the picking.

Moreover, when the picking gets cancelled, the split lines are merged back into
their origin line.
