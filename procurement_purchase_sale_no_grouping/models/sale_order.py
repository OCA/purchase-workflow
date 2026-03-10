# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_create(self, quantity=False):
        no_grouped_lines = self.filtered(
            lambda sol: (sol.product_id.categ_id.procured_purchase_grouping == "order")
        )
        res = super(SaleOrderLine, self - no_grouped_lines)._purchase_service_create()
        res.update(
            super(
                SaleOrderLine,
                no_grouped_lines.with_context(search_purchase_no_grouping=True),
            )._purchase_service_create()
        )
        return res
