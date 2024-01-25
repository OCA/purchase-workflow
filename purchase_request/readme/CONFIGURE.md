To configure the product follow this steps:

1.  Go to a product form.
2.  Go to *Inventory* tab.
3.  Check the box *Purchase Request* along with the route *Buy* and *Replenish on Order (MTO)*

Note that MTO route is archived by default, you should unarchive it first:
- Go to Inventory > Configuration > Routes, in the Search dropdown menu, click *Archived* to show *Replenish on Order (MTO)* route and *Unarchive* it.

With this configuration, whenever a procurement order is created and the
supply rule selected is 'Buy' the application will create a Purchase
Request instead of a Purchase Order.
