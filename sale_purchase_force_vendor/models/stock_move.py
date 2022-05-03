# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        """Inject the preferred vendor in case of a MTO that first creates the OUT
        move.
        """
        res = super()._prepare_procurement_values()
        if self.sale_line_id.vendor_id:
            res_order_line = self.sale_line_id._prepare_procurement_values(
                group_id=self.group_id
            )
            res.update({"supplierinfo_id": res_order_line["supplierinfo_id"]})
        return res
