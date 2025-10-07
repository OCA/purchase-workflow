When a purchase order is confirmed, the value of the received goods is updated upon
reception. It can happen anyway that the reception of the goods is confirmed before
the final price is recorded in the corresponding purchase line.

For that, Odoo will fix the valuation when the invoice for that purchase is confirmed,
but that moment could be delayed for an uncertain period of time while thos stored
goods are being selled with wrong margins and the value being discounted for a wrong
price unit.

We want to fix those disalignments as soon as possible from the purchase order while
keeping the native mechanism to add later corrections from the invoice itself.
