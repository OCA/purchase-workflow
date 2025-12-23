Purchase billing contact
-------------------

- Go to *Purchase* > *Orders* > *Vendors*
- Select or create a supplier.
- Go to the Contacts and Addresses tab, add a new one,
  select the *Purchase invoice address* type, and fill in the *email* field.
  ![ADDRESS_PURCHASE](../static/img/readme/ADDRESS_PURCHASE.png)
- Save the contact.

Select a billing address on purchase orders
-------------------

- Go to *Purchase* > *Orders* > *Request for Quotation*
- Select or create a purchase order.
- Select a supplier. If they have a *Purchase invoice address*,
  the first option will be displayed, but you can change the default.
  ![SELECT_ADDRESS_PURCHASE](../static/img/readme/SELECT_ADDRESS_PURCHASE.png)
- Complete all other fields in the order.
- Confirm the order.
- When creating the invoice, check whether a billing address is selected and assign it to the invoice.
  If not, follow the normal Purchase Order process.
  ![PURCHASE_INVOICE](../static/img/readme/PURCHASE_INVOICE.png)

Billing address selection order.
-------------------

1. First, we search to see if there is a *Purchase invoice address* type contact among the selected supplier's contacts.
2. If none exist in the previous step, the supplier's contacts, i.e., secondary contacts, are searched using the same
   criteria as above.
3. If none are met, the same supplier is selected.
