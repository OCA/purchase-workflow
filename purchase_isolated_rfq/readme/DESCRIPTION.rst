Note: This module is similar to sale_isolated_quotation, but for purchase/rfq

In some countries/companies, It's already common to separate these two documents.
For filing purposes, the document sequence of Requests For Quotation (RFQ) and Purchases order
has to be separated. In practice, there could be multiple RFQ open
to a vendor, yet only one RFQ get converted to the Purchases order.

This module separate RFQ and Purchases order by adding order_sequence flag in
purchase.order model.

Each type of document will have separated sequence numbering.
RFQ will have only 2 state, Draft and Done. Purchases Order work as normal.
