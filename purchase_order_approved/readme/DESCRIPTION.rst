This module extends the functionality of purchases adding a new state
*Approved* in purchase orders before the *Purchase Order* state. Additionally
add the possibility to set back to draft a purchase order in all the states
previous to *Purchase Order*.

In this new *Approved* state:

* You cannot modify the purchase order.
* However, you can go back to draft and pass through the workflow again.
* The incoming shipments are not created. You can create them by clicking the
  *Convert to Purchase Order* button, also moving to state *Purchase Order*.

The new state diagram is depicted below:

.. image:: purchase_order_approved/static/description/schema.png
   :width: 500 px
   :alt: New states diagram
