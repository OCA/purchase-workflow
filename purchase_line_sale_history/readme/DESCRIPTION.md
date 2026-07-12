This module lets purchasers consult the sales history of a product while
filling a purchase order, without leaving the order form.

Each purchase order line gets a *Sales History* checkbox. When checked, a
pivot table is displayed below the order lines with the quantities of that
product sold per month (columns) and year (rows), based on posted customer
invoices (credit notes are subtracted). Only one line per order can be
active at a time.

The history is computed for the exact product variant of the line, so
different variants of the same product template are never mixed.
