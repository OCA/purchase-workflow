To use this module, you need to:

#. Create a new purchase order.
#. Assign its supplier.
#. Press *Recommended Products* button.
#. Set or adjust hinted quantities to order.
#. Press *Accept*.

The wizard filters products those with supplier infos set for the current order
supplier. Then it computes how many times those products have been delivered to
customer locations, and finally it makes a simple estimation of how many
quantites would be necesary to order given the forcasted stock and the computed
demand.

If you want to constrain results to only some categories, you can also select
them in the wizard.

If you have multiple warehouses, you can also constrain the recommendations to
the deliveries of specific ones.
