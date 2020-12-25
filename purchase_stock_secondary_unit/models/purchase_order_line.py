# Copyright 2020 Jarsa Sistemas
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class PurchaseOrderline(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        for move in res:
            if move.get("purchase_line_id"):
                purchase_line = self.env["purchase.order.line"].browse(
                    move["purchase_line_id"]
                )
                if purchase_line.secondary_uom_id:
                    move.update(
                        {
                            "secondary_uom_id": purchase_line.secondary_uom_id.id,
                            "secondary_uom_qty": purchase_line.secondary_uom_qty,
                        }
                    )
        return res
