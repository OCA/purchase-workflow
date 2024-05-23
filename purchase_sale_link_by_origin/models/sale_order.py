# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("origin")
    def _compute_purchase_order_count(self):
        return super()._compute_purchase_order_count()

    def _get_purchase_orders(self):
        po_related = self.env["purchase.order"]
        for order in self:
            po_related |= self.env["purchase.order"].search(
                [("origin", "ilike", order.name)]
            )
        return super()._get_purchase_orders() | po_related
