# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def get_valuation_lines(self):
        """
        We redo the get_valuation_lines() function from odoo core because there
        is no other way to avoid records with real_time.
        """
        lines = []
        for move in self.mapped("picking_ids").mapped("move_lines"):
            if (
                move.product_id.cost_method not in ("fifo", "average")
                or move.state == "cancel"
                or not move.product_qty
            ):
                continue
            vals = {
                "product_id": move.product_id.id,
                "move_id": move.id,
                "quantity": move.product_qty,
                "former_cost": sum(move.stock_valuation_layer_ids.mapped("value")),
                "weight": move.product_id.weight * move.product_qty,
                "volume": move.product_id.volume * move.product_qty,
            }
            lines.append(vals)

        if not lines and self.mapped("picking_ids"):
            raise UserError(
                _(
                    "You cannot apply landed costs on the chosen transfer(s)."
                    "Landed costs can only be applied for products with "
                    "FIFO or average costing method."
                )
            )
        return lines


class AdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _create_accounting_entries(self, move, qty_out):
        if self.product_id.valuation != "real_time":
            return self.env["account.move.line"]
        return super()._create_accounting_entries(move, qty_out)
