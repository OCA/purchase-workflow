This module extends the odoo purchase module, to remove 'Request for
Quotation' state, simplifying the workflow for the end users.

Once installed :

- The menu item 'Purchase > Orders > Requests for Quotation' is hidden 
for regular users (it is only visible with technical features). 
A single menu item 'Purchase Orders' is available and shows all the 
orders, whatever their state.
- The states names of the purchase order is altered. 'RFQ' is replaced
  by 'Draft' and 'RFQ sent' by 'Sent'.
- The colors in the tree view is correctly set to `decoration-info` for
  'draft' and 'sent' orders.
- In the form view, the 'Request for Quotation' title is replaced by 
'Purchase Order' and the buttons 'Send RFQ' are renamed 'Send by Email'.
- The 'Print' button always prints the 'Purchase Order' report, 
whatever the state of the order. The option 'Print > Request For quotation' 
is also disabled.
