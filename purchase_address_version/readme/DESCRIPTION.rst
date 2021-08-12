This module uses the partner_address_version module to create a fixed address version when confirming a purchase order.

By default, this module ensure that the address field (partner_address_id) is immutable.
This works by ensure that, whenever a purchase order is confirmed, the address fields of the purchase order will be copied (and immediately archived), so it will used by this purchase order only.
