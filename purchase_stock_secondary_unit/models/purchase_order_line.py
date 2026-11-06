# Copyright 2020 Jarsa Sistemas
# Copyright 2021 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.tools.float_utils import float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):
        if "secondary_uom_qty" not in vals:
            return super().write(vals)
        po_lines = self.filtered(
            lambda ln: ln.secondary_uom_qty != vals["secondary_uom_qty"]
        )
        res = super().write(vals)
        for po_line in po_lines:
            moves = po_line.move_ids
            if len(moves) == 1:
                moves.filtered(lambda sm: sm.state not in ["done", "cancel"]).write(
                    {"secondary_uom_qty": vals["secondary_uom_qty"]}
                )
            elif moves and vals.get("secondary_uom_qty"):
                previous_secondary_qty = sum(m.secondary_uom_qty for m in moves[:-1])
                moves[-1:].filtered(
                    lambda sm: sm.state not in ["done", "cancel"]
                ).secondary_uom_qty = vals["secondary_uom_qty"] - previous_secondary_qty
        return res

    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ):
        vals = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        if self.secondary_uom_id:
            vals["secondary_uom_id"] = self.secondary_uom_id.id
            if self.secondary_uom_id.dependency_type == "independent":
                vals["secondary_uom_qty"] = self.secondary_uom_qty
            else:
                # A line may generate several moves or only an additional receipt.
                # Convert each move quantity, rather than copying the line total.
                qty = product_uom._compute_quantity(
                    product_uom_qty, self.product_id.uom_id, round=False
                )
                vals["secondary_uom_qty"] = float_round(
                    qty / (self.secondary_uom_id.factor or 1.0),
                    precision_rounding=self.secondary_uom_id.uom_id.rounding,
                )
        return vals

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        po,
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            po,
        )
        res["secondary_uom_id"] = values.get("secondary_uom_id", False)
        res["secondary_uom_qty"] = values.get("secondary_uom_qty", 0.0)
        return res
