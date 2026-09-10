This module allows users to select multiple purchase order lines from
different purchase orders and merge them into a single new purchase order.

Unlike `purchase_merge` which works at the order level, this module
operates at the line level, giving more granular control over which
specific lines to consolidate.

Key features:

- Lines with the same product, unit price, unit of measure, and taxes are
  automatically grouped into a single line on the resulting purchase order.
- The default quantity to merge considers both invoiced and received
  amounts, defaulting to the available (uninvoiced/unreceived) quantity.
- The unit price is editable in the wizard, allowing price adjustments
  before creating the new order.
- Partial merges are supported: the remaining quantity stays on the
  original order.
- Orders that reach zero amount after the merge are automatically
  cancelled.

This module also adds the **Qty Invoiced** and **Qty Received** columns
to the Purchase Order Lines list view for better visibility.
