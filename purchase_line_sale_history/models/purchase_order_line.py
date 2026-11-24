# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    show_sales_history = fields.Boolean(
        string="Sales History",
        copy=False,
        help="Show the sales history of this line's product below the "
        "order lines. Only one line per order can be active at a time.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.filtered("show_sales_history")[-1:]._activate_sales_history()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if vals.get("show_sales_history"):
            self[-1:]._activate_sales_history()
        elif "show_sales_history" in vals:
            self.order_id.filtered(
                lambda order: order.sales_history_line_id in self
            ).sales_history_line_id = False
        return res

    def _activate_sales_history(self):
        for line in self:
            (line.order_id.order_line - line).filtered(
                "show_sales_history"
            ).show_sales_history = False
            line.order_id.sales_history_line_id = line
