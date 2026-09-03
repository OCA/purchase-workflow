**Provide tools to help a purchaser during the purchase process.**

- Go to **Purchase > Purchase > Computed Purchase Order**, Create a new Compute Purchase Order (CPO)
- Select a Supplier
- Check the boxes to tell if you want to take into account the virtual stock or the draft sales/purchases.
- Use the button 'Get products and stocks' to import the list of products you can purchase to this supplier (ie: products that have a product_supplierinfo for this partner). It especially calculates for each product:
    - the quantity you have or will have;
    - the average_consumption, based on the stock moves created during last 365 days;
    - the theoretical duration of the stock, based on the precedent figures.

- Unlink the products you don't want to buy anymore to this supplier (this only deletes the product_supplierinfo)
- Click the "Update Products" button to register the changes you've made into the product supplierinfo.
- Check the Purchase Target. It's defined on the Partner form, but you still can change it on each CPO.
- Click the button 'Compute Purchase Quantities' to calculate the quantities you should purchase. It will compute a purchase order fitting the purchase objective you set, trying to optimize the stock duration of all products.
- Click the "Make Purchase Order" button to convert the calculation into a real purchase order.


Possible Improvements:
- offer more options to calculate the average consumption;
