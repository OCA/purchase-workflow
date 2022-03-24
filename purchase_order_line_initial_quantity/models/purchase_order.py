# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    initial_qty_changed = fields.Boolean(
        string="Initial Quantity Changed",
        compute="_compute_initial_qty_changed",
        store=True,
    )

    @api.depends("order_line", "order_line.product_qty")
    def _compute_initial_qty_changed(self):
        for order in self:
            order.initial_qty_changed = order.state in ["purchase", "done"] and bool(
                order.order_line.filtered(
                    lambda l: l.product_qty != l.product_initial_qty
                )
            )

    def button_confirm(self):
        res = super().button_confirm()
        for line in self.order_line:
            line.product_initial_qty = line.product_qty
        return res
