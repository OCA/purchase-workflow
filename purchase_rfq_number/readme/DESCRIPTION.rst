Note: This module is similar to sale_quotation_number, but for purchase/rfq

* Purchase for Quotation:

  * Purchase process in draft stage just informing prices and element of communication.

* Purchase Order:

  * Purchase process confirmed, the customer already have a compromise with us in terms of pay an invoice and receive our product or service.

**Technical Explanation**

When you create a purchase quotation, it is numbered using the 'purchase.rfq'
sequence.  When you confirm a purchase quotation, its rfq number is saved in the
'rfq_number' field and the purchase order gets a new number, retrieving it from
'purchase.order' sequence.

* With Odoo Base:

    Purchase for Quotation 1 Number = PO001

    Purchase for Quotation 2 Number = PO002

* With Odoo + This Module:

    Purchase for Quotation 1 Number = RFQ001

    Purchase for Quotation 2 Number = RFQ002

    Purchase for Quotation 1 Confirmed = Number for Purchase Order PO001 from Purchase for Quotation RFQ001

    Purchase for Quotation 2 Confirmed = Number for Purchase Order PO002 from Purchase for Quotation RFQ002
