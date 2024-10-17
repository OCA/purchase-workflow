# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # This field is more complete than the standard is_shipped
    is_fully_shipped = fields.Boolean(
        compute="_compute_is_fully_shipped", store=True, index=True
    )

    @api.depends("order_line.qty_received")
    def _compute_is_fully_shipped(self):
        for purchase in self:
            if all(
                line.product_qty <= line.qty_received for line in purchase.order_line
            ):
                purchase.is_fully_shipped = True
            else:
                purchase.is_fully_shipped = False
