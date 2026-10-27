Every warehouse gets an **Incoming transit** location and a **Transit
receipt** operation type. A purchase using this operation type is
received in two or more steps:

1.  the Transit receipt, from the vendor to the Incoming transit, when
    the vendor ships the goods;
2.  the usual reception of the warehouse (one, two or three steps),
    created by a push rule when the Transit receipt is done.

The Incoming transit is a transit location of the warehouse's company,
outside the warehouse: goods in transit are valued and counted in the
inventory, but they are neither available nor reservable.

This is the design inspired by `stock_route_transit` (OCA
stock-logistics-transport, 8.0 to 10.0), without new reception steps.
