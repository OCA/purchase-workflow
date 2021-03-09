Set the Purchase Approval Block
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Go to 'Purchases / Purchase / Requests for Quotation'
#. Create a new RFQ and upon saving if the Untaxed Amount is below the
   Purchase Minimum Amount specified in that vendor, then the Approval Block
   Reason is automatically set and the Approval Block Reason is not editable
   anymore.

Search existing RFQ
~~~~~~~~~~~~~~~~~~~

There is a filter 'Blocked' to search for orders that are blocked.
It is also possible to search RFQ’s with the Approval Block Reason 'Minimum
Purchase Order Amount per Vendor'.

Confirm the RFQ
~~~~~~~~~~~~~~~

#. Press the button ‘Confirm’. If there’s an approval block, the order will
   be set to status 'To Approve'. You will then need to request a Purchase
   Manager to approve it.

Release the purchase approval block
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. All the RFQ’s with a total amount surpassing the specified Minimum Purchase
   Order Amount for that vendor (excluding taxes) are automatically released.
#. If a blocked RFQ without surpassing the minimum amount wants to be
   released, a user member of the security group 'Release RFQ with approval
   block' can see a button 'Release Approval Block'. When pressing it, anyone
   seeing that RFQ is able to validate it.

Notifications to followers
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Followers of the RFQ receive notifications when an approval block has been
   set or released.
