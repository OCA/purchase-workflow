- Create new purchase quotation as per normal process
- Select option "Use Invoice Plan", a new Invoice Plan tab will appear
- Click on "=\> Create Invoice Plan" link to open invoice planning
  wizard
- Do plan for number of installment, start date and interval
- Double check that each installment has correct plan percentage
- After confirm purchases order, we have new option to "Create Bill by
  Plan"
- User can create only next bill or create all bills at the same time

Bills created by the standard flows also follow the invoice plan: "Create
Bills" from the purchase order list, "Upload Bill", a vendor bill
auto-completed from the purchase order, or Bill Matching.

- The bill uses the next installment not billed yet; all lines of the same
  purchase order in a bill use the same installment
- Lines created from the purchase order get the installment quantity, but
  never more than the quantity to bill of the standard
- Lines imported from a vendor document (EDI, matching with an existing
  bill line) keep their quantity and are only linked to the installment
- The bill date is the installment date, as with "Create Bill by Plan",
  unless the bill already has a date (e.g. typed before the auto-complete,
  or from the vendor document)
- The installments of a bill are shown in its header, and the installment
  of each bill line in the optional column "Invoice Plan" of the bill lines

Down payments added to the purchase order (Bill Matching > Add to PO > Add
Down Payment) are deducted in proportion of each installment, as in
sale_invoice_plan: an installment of 20% deducts 20% of the down payments, a
partial bill of the installment deducts in proportion of the billed amount, and
the last installment deducts the remaining down payment.
