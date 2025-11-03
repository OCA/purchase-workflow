This module adds a new field to purchase order lines:

| Technical name        | Type      | Scope         | Purpose |
|-----------------------|-----------|---------------|---------|
| `line_receipt_status`  | Selection | PO Line       | Indicates the reception status of the purchase line, based on the state of its pickings. |

Allowed values:

| Value      | Label            | Business meaning |
|------------|-----------------|-----------------|
| None       | (not set)       | No reception activity |
| `pending`  | Not Received     | No pickings done yet |
| `partial`  | Partially Received | Some pickings are done but not all |
| `full`     | Fully Received   | All pickings are done or cancelled |

## Behavior

- Computed from the pickings associated with the line.  
- Preserves the same logic and semantics as the standard `purchase.order.receipt_status`.  
- Complementary to quantity-based modules (e.g., `purchase_reception_status`) without interfering with them.