# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderLinePriceHistoryLine(models.TransientModel):
    _inherit = "purchase.order.line.price.history.line"

    discount = fields.Float(related="purchase_order_line_id.discount")

    def _prepare_purchase_order_line_vals(self):
        vals = super()._prepare_purchase_order_line_vals()
        vals.update(discount=self.discount)
        return vals
