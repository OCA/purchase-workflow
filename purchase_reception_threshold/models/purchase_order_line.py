# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    receipt_threshold = fields.Float(
        related="order_id.receipt_threshold",
    )
    use_threshold = fields.Boolean(
        related="order_id.use_threshold",
    )

    def _check_threshold(self, quantity):
        """Check if `quantity` is within threshold limits.

        This method calculates the minimum and maximum threshold quantities
        based on the purchase order line's product quantity
        and receipt threshold percentage.
        It then checks if the received quantity falls within these limits.

        :param quantity: The quantity received for this purchase order line.
        :return: True if the received quantity is within the threshold limits,
                 False otherwise.
        """
        self.ensure_one()
        if self.use_threshold and self.receipt_threshold:
            threshold = self.product_uom_qty * self.receipt_threshold
            threshold_min = self.product_uom_qty - threshold
            threshold_max = self.product_uom_qty + threshold
            return threshold_min <= quantity <= threshold_max
        return False
