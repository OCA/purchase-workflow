# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_requisition_line(
        self, product_id, product_qty, product_uom, values
    ):
        line_vals = super()._prepare_purchase_requisition_line(
            product_id, product_qty, product_uom, values
        )
        # propagate sale_line_id to requisition line
        # to propagate it to the purchase order line later
        if values.get("sale_line_id"):
            line_vals["sale_line_id"] = values.get("sale_line_id")
        return line_vals
