* In vendor, enable **Use Product Components** option in the **Sales & Purchases** tab.
* In product, enable **Use Product Components** option in the **Purchase** tab.
* If both product and vendor have the flag activated, in the **Purchase** tab of the **Product**, table **Vendor** there will be a button at the end of the supplierinfo line.
* Click the button and add components and quantities to display in vendor bill for the product > save
* Supplierinfo price is now readonly and calculated as sum of the first applicable supplierinfo price * their quantities.
* Create a new RQF from this Vendor, add product with breakdown components.
* Confirm the RFQ. Note there will be a button for the product component breakdown in the PO Lines, tracking qty received and billed.
* When a vendor bill is created, only received components are billed and not the product in the PO Line.
