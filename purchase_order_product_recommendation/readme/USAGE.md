To use this module, you need to:

1.  Create a new purchase order.
2.  Assign its supplier.
3.  Press *Recommended Products* button.
4.  Set or adjust hinted quantities to order.
5.  Press *Accept*.

The wizard filters products those with supplier infos set for the
current order supplier. Then it computes how many times those products
have been delivered to customer locations, and finally it makes a simple
estimation of how many quantites would be necesary to order given the
forcasted stock and the computed demand.

If you want to constrain results to only some categories, you can also
select them in the wizard.

If you have multiple warehouses, you can also constrain the
recommendations to the deliveries of specific ones.
