# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        """Inject the preferred vendor in case of an MTO that first creates the OUT
        move.
        """
        res = super()._prepare_procurement_values()
        # Get all chained moves to get sale line
        moves = self.browse(list(self._rollup_move_dests({self.id})))
        move_sale = moves.filtered("sale_line_id")[:1]
        if move_sale.sale_line_id.vendor_id:
            res_order_line = move_sale.sale_line_id._prepare_procurement_values(
                group_id=move_sale.group_id
            )
            res.update({"supplierinfo_id": res_order_line["supplierinfo_id"]})
        return res
