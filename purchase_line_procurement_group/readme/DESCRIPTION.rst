This module changes the way procurements generate purchase order lines.
If some procurements are run for the same products and locations, but have
different procurement groups, these won't be merged in the same purchase order
line and will instead generate a purchase order line per procurement group.

Moreover this module ensures that generated stock move won't be merged together
if they come from purchase order lines with different procurement groups.
