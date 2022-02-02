This module adds a new selection field ``receipt_expectation`` to
``purchase.order``. By default, its value is ``"automatic"``, which means
that the picking creation at order approval is managed by the Odoo standard
workflow.

Inheriting modules can extend the selection field with a custom value, but this
will also require to define a custom method named ``_create_picking_for_<value>_receipt_expectation()``
on ``purchase.order`` to manage picking creation for orders with the new field
value, else a ``NotImplementedError`` will be raised.

For example:

.. code-block:: python

  class PurchaseOrder(models.Model):
      _inherit = "purchase.order"

      receipt_expectation = fields.Selection(
          selection_add=[("my_value", "My Value")],
          ondelete={"my_value": "set default"},
      )

      def _create_picking_for_my_value_receipt_expectation(self):
          """Manage picking creation for orders where ``receipt_expectation``
          is ``"my_value"``
          """
          ...
