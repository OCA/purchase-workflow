# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends(
        "state", "force_received", "order_line.qty_received", "order_line.product_qty"
    )
    def _compute_receipt_status(self):
        # Use the OCA logic instead of the native picking-based logic
        self._compute_oca_receipt_status()
