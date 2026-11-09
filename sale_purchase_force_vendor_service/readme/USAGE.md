1.  Go to *Sales \> Products \> Products* and open a service product.
2.  Check "Subcontract Service" and, in the *Purchase* tab, set several
    vendors (e.g. Vendor A and Vendor B).
3.  Create a quotation with this product and select a vendor in the
    *Vendor* column of the line (hidden by default in the list).
4.  Confirm the quotation. A request for quotation is created for the
    selected vendor. If no vendor is selected, the first vendor of the
    product is used. If the selected vendor has no price line matching
    the line, one is created for it, as `sale_purchase_force_vendor`
    does for the stock route.
