Odoo computes the quantity to accrue as *received at date − billed at date*.
Received quantities use the effective date of the stock moves, but billed
quantities use the bill date, not the accounting date.

When a bill has a bill date inside the period but is posted with an
accounting date in the next period, and the goods are also received in the next
period, the accrual is negative: it credits the expense account. When that
entry is reversed in the next period, together with the real bill, the expense
is counted twice.

Using the accounting date for both sides keeps the accrual consistent with
what is really booked in the ledger at the closing date.
