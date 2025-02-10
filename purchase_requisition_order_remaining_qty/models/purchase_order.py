# Copyright 2021-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        """In this function the lines are added to the order. At the end we will
        auto-delete the lines with quantity 0."""
        result = super()._onchange_requisition_id()
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        self.order_line -= self.order_line.filtered(
            lambda x: float_is_zero(x.product_qty, dp)
        )
        return result
