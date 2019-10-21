#. User configuration:

    * Go to **Settings > Users**
    * Select a user and check the **Suppliers approval** group

#. Pending state configuration:

    By default, the *Pending approval* state is not a blocking state.

    This can be configured by going to **Settings > System Parameters**
    and modifying the value of the **supplier_approval.pending_block** parameter:

    * 0 (default) - the pending approval state does not block purchase order confirmation.
    * 1 - the pending approval state blocks purchase order confirmation.
