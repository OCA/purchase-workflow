Once auto-billing is configured, validate a purchase receipt as usual.
A Vendor Bill is automatically created and posted shortly after via the
scheduled action. The bill only includes PO lines whose product bill
control policy is *On received quantities* and that have a positive
quantity to invoice.

**Returns / Credit Notes:** When a return is validated and its return
lines have *Update quantities on SO/PO* enabled in the return wizard, a
Credit Note is automatically created and posted for the returned
quantities. The credit note is only created when a Vendor Bill has
already been posted (i.e. the PO line has a negative *Quantity to
Invoice*).

The bill/credit note date is the receipt/return validation date converted
to the company's timezone (falls back to UTC when no timezone is set).

If creation or posting fails, the error is logged in the Purchase
Order chatter and a To-Do activity is scheduled for follow-up.

**Case 1 — Cancelling an auto-bill:** An auto-posted bill can be
cancelled like any other Vendor Bill. However, the module will not
automatically create a new bill for the same receipt.

**Case 2 — Reprocessing an auto-bill:** This is not supported. Once the
scheduled action processes a receipt or return, it will not be picked up
again. To bill or refund the same quantities, create the document
manually from the Purchase Order.
