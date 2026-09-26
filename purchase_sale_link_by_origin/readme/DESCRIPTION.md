By default since [Odoo 14.0](https://github.com/odoo/odoo/commit/5a1645a8f8f3560eb778da90b6160b322ce0722e), PO and SO are linked by their order lines.

This module also link them by the PO's Origin field, to cover more cases. For example:
- If a user cancels a PO, by default the link would have been broken; now it won't;
- Or if a user manually defines or updates the Origin field of a PO, it will be taken into account.
