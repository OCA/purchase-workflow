This module is automatically installed when both purchase_reception_status and
purchase_stock are present in the system.

No additional configuration is required. The module will automatically:

1. Override the native receipt_status computation method
2. Apply the OCA logic for calculating purchase order reception status
3. Hide duplicate receipt_status fields in views to avoid confusion

The purchase order will continue to display the receipt_status field with
values "pending", "partial", and "full", but computed using the OCA logic.

Users can continue to use the force_received flag to manually mark orders
as fully received when needed.
