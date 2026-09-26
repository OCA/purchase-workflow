# Copyright 2023 Camptocamp SA
# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("origin")
    def _compute_sale_order_count(self):
        return super()._compute_sale_order_count()

    def _get_sale_orders(self):
        origins = set()
        for order in self:
            if order.origin:
                for origin_part in order.origin.split(", "):
                    if " - " in origin_part:
                        origins.add(origin_part.split(" - ")[-1].strip())
                    else:
                        origins.add(origin_part.strip())
        so_origins = self.env["sale.order"].search([["name", "in", list(origins)]])
        return super()._get_sale_orders() | so_origins
