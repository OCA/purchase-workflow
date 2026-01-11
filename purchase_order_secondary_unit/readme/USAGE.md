To use this module you need to:

1.  Go to a *Product \> General Information tab*.
2.  Create any record in "Secondary unit of measure".
3.  Set the conversion factor.
4.  Go to *Purchase \> Quotation \> Create*.
5.  Change secondary qty and secondary uom in line, and quantity
    (product_qty) will be changed (according to the conversion factor).

**Vendor Pricelist Integration**

-   When adding a vendor to a product's pricelist (via *Purchase tab > Vendors*), the
    secondary unit of measure is automatically defaulted from the product variant's
    purchase secondary UOM, or from the product template if not set on the variant.
-   When a new vendor pricelist record is created from purchase order confirmation, the
    secondary UOM from the purchase order line is automatically stored in the vendor
    pricelist entry.
