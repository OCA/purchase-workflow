In order to test the module:

- Go to *Purchase > Orders* and create a new quotation.
- Add a product with AVCO valuation and set a price.
- Validate the purchase order.
- Receive the products.
- The products are now valued at the price you set in the order line.
- You can check it in *Inventory > Reporting > Valuation* (debug mode needed).
- Now change the price in the order line.
- You'll see that the line has changed its color to yellow and a new button
  *Fix valuation* shows up in the header.
- When you click that button, every disaligned valuation will be fixed. If you go to the
  *Valuation* report you'll see the adjustment layer.
