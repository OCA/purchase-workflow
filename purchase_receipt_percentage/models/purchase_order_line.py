# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    receipt_percentage = fields.Float(compute="_compute_receipt_percentage", store=True)

    @api.depends("qty_received", "product_qty")
    def _compute_receipt_percentage(self):
        for line in self:
            perc = 100  # 100% by default, in case ordered qty is 0
            if not float_is_zero(
                line.product_qty, precision_rounding=line.product_uom.rounding or 2
            ):
                perc *= line.qty_received / line.product_qty
            line.receipt_percentage = min(max(perc, 0), 100)  # 0 <= % <= 100
