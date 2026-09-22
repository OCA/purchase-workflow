This module lets you select, on each purchase order, the address of your **own**
company to which the vendor should send the invoice, and prints it on the
purchase order report.

Odoo links a company to a single partner record, so a company operating from
several locations has no standard place to hold more than one of its own
addresses. This module reuses the child addresses of the company partner for
that purpose: the head office (the company partner itself) and any of its
address records can be selected per purchase order.

The selected address is carried over to the vendor bills created from the
purchase order.
