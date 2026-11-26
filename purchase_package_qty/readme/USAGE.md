Go to **Purchase > Products**, open one product, and edit or add a record on
the **Vendors** section of the **Purchase** tab. You will see in the prices
section in the down part a new column called **Packaging**. You can enter
here the seller's Packaging.

![2_product_supplierinfo](../static/img/2_product_supplierinfo.png)

You can assign the Price Policy too. It's per UOM or per Package.

Based on Price policy the amount will be calculated.
    * If you choose per UOM then it will be the default calculation.
    * If you choose per Package then it will consider the quantity of **Packaging Quantity** column

![3_purchase_order](../static/img/3_purchase_order.png)

**Packaging** and **Packaging Quantity** columns will be forwarded to Incoming shipment when you confirm the PO.
Same way **Packaging**, **Packaging Quantity** and **Price Policy** will be forwarded to Vendor bills when you Create an invoice from PO.
