# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2022 Tecnativa - Víctor Martínez
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
            # When the affected product is a kit we do nothing, which is the
            # default behavior on the standard: the move is exploded into moves
            # for the components and those get the default price_unit for the
            # time being. We avoid a hard dependency as well.
            if hasattr(line.product_id, "bom_ids") and self.env[
                "mrp.bom"
            ].sudo()._bom_find(
                product=line.product_id,
                company_id=line.company_id.id,
                bom_type="phantom",
            ):
                continue
            # We check if the stock_landed_costs addon is installed to exclude linked
            # records.
            stock_valuation_layers = line.move_ids.mapped("stock_valuation_layer_ids")
            if hasattr(line.product_id, "landed_cost_ok"):
                stock_valuation_layers = stock_valuation_layers.filtered(
                    lambda x: not x.stock_landed_cost_id
                )
            stock_valuation_layers.write(
                {
                    "unit_cost": line.with_context(
                        skip_stock_price_unit_sync=True
                    )._get_stock_move_price_unit(),
                }
            )
