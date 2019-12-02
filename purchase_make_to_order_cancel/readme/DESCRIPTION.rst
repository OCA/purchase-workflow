This module presents a solution to the possibility of a purchase cancellation
with a Make To Order (MTO) product. In Odoo v11 and v12 the cancellation of
the generated and confirmed purchase automatically cancels the stock picking
of the sale, without any warning or activity.

The core of the problem is that the purchase move has been created with
propagate=True (by default, as it is not informed), and therefore the sale
move is cancelled when the purchase is cancelled.

So this module deals with this problem with two actions:

* Inform the propagate field in the purchase move with the value of the procurement rule that created it. That way we can configure it on UI as False, and therefore the sale move won´t be cancelled - module stock will just change it to MTS
* Upon cancelling the purchase: recompute the state of the sale move, so it will change from "Waiting for other operation" to "Waiting availability"
