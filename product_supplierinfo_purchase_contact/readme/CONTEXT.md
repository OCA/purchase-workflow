This module had 2 purposes:
- To specify which contact the purchase orders generated from procurements associated to this supplierinfo have to be put.
- That the auto-created supplierinfo from the purchase order has the main partner associated, not the specific contact one.

The 'Purchase contact' (purchase_partner_id) field is required if for example you use sales pricelist based on supplierinfo
(product_pricelist_supplierinfo), you want to use as supplier filter the 'Supplier' (partner_id) field.