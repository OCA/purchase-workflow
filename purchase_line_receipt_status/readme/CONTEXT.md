In standard Odoo, the `purchase.order` model provides a `receipt_status` field
to track the reception of purchase orders. This field is computed based on the
associated pickings:

- None: No pickings created or all pickings cancelled
- `pending`: Not received yet
- `partial`: Some pickings done
- `full`: All pickings done (even if some were cancelled)

However, there is **no equivalent status at the purchase order line level**.  
This module introduces the missing `line_receipt_status` field on purchase order lines,
using the same logic as the standard PO `receipt_status`.

It complements OCA modules such as `purchase_reception_status` without modifying
their quantity-based logic. This module preserves the original picking-based
status computation, ensuring consistency with Odoo’s standard behavior.