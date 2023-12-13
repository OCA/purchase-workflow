To use this module, you need to:

Manual order:

  #. Go to Purchase > Orders > Vendors.
  #. Create a new vendor and set Purchase Manager in Sales & Purchases tab.
  #. Go to Purchase > Orders > Purchase Orders.
  #. Set Vendor created before.
  #. Buyer is fill automatically with value in purchase manager from vendor. As long as the quotation is not confirmed or locked the "buyer" field will be updated if the value of the vendor's "Purchase Manager" field is changed by copying that value.
  #. Confirm the Purchase Order.
  #. Change Purchase Manager in Vendor.
  #. Buyer in Purchase Order has not changed. All purchase orders in "Purchase" or "Done" status will not update the value of the "buyer" field even if the value of the "Purchase Manager" field in the vendor is changed.

Replenishment order:

  #. When a replenishment order is executed the "buyer" field of the RFQ will copy the value of the "Purchase Manager" field assigned to the vendor.
  #. Afterwards, the operation will be the same as in the Manual order case:
