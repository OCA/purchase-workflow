This module extends ``purchase_receipt_expectation`` by adding the
``receipt_expectation`` field to ``res.partner`` and filling the same field on
``purchase.order`` via the partner's field.

Once a purchase order is created, the PO's ``receipt_expectation`` will be
filled via an onchange from the partner's field (if set).
