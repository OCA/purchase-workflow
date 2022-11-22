The standard fields is_shipped and invoice_status show information about the status
of the shipments and invoices related to a Purchase Order.

However, it can be than the field is_shipped is marked as True when some of the shipments
were cancelled. At the same time, the invoice status can be "invoiced" when the invoices
are still in draft. Many times that makes the difference to consider the Purchase Order
as closed or not. Because of this, this module introduce two new fields that  will show
that the Purchase Order is fully Shipped and Fully Invoiced, taking the state into
account.
