Whether a Purchase Order is auto-billed when its receipt is validated is
resolved from two configuration levels, plus a per-order kill switch:

1. **Company** → *Settings > Purchase > Invoicing > Auto Bill on Receipt*
   (boolean). Sets the default for all vendors.
2. **Vendor** → *Auto Bill on Receipt* (selection: *Auto* / *No Auto* /
   empty), on the vendor form. Leave empty to inherit from the company.
   *Auto* or *No Auto* overrides the company default for this vendor.
3. **Purchase Order** → *Block Auto Bill* (boolean, on the *Other
   Information* tab). When ticked, suppresses auto-billing for this order
   regardless of the company or vendor settings.

The bill date uses the timezone set on the company's contact. To set it,
install the
[partner_tz](https://github.com/OCA/partner-contact/tree/19.0/partner_tz)
module and configure the timezone on the company's contact.
