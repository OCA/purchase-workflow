# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):
        res = super().write(vals)
        if ("price_unit" in vals or "discount" in vals) and (
            not self.env.context.get("skip_stock_price_unit_sync")
        ):
            self.stock_price_unit_sync()
        return res

    def stock_price_unit_sync(self):
        for line in self.filtered(lambda l: l.state in ["purchase", "done"]):
            line.move_ids.mapped("stock_valuation_layer_ids").write(
                {
                    "unit_cost": line.with_context(
                        skip_stock_price_unit_sync=True
                    )._get_stock_move_price_unit(),
                }
            )
