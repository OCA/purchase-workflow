The standard field is_shipped show information about the status
of the shipments and invoices related to a Purchase Order.

However, it can be than the field is_shipped is marked as True when some of the shipments
were cancelled. Because of this, this module introduce a new field that  will show
that the Purchase Order is fully Shipped.
