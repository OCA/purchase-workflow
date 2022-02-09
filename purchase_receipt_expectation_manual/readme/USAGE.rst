This module extends ``purchase_receipt_expectation`` by managing manual
receipts.

Purchase orders where ``receipt_expectation`` is set to ``manual`` will not
generate any incoming picking when validated. Users will then be able to
generate pickings manually using the ``Receive`` button in the order form view.
It will open a wizard that allows users to define which order products are
being received, their quantity and unit price, and the scheduled date of the
picking.

Once user confirms the wizard action, a new picking will be created with chosen
products and quantities.
