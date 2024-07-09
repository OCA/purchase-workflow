# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ):
        res = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        bom = (
            self.env["mrp.bom"]
            .sudo()
            ._bom_find(
                self.product_id, company_id=self.company_id.id, bom_type="distribution"
            )[self.product_id]
        )
        if bom:
            res["distribution_bom_id"] = bom.id
        return res

    def _get_po_line_moves(self):
        res = super()._get_po_line_moves()
        bom = (
            self.env["mrp.bom"]
            .sudo()
            ._bom_find(
                self.product_id, company_id=self.company_id.id, bom_type="distribution"
            )[self.product_id]
        )
        res |= self.move_ids.filtered(
            lambda m: m.product_id in bom.bom_line_ids.product_id
        )
        return res
