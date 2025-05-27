# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        """ """
        domain = super()._make_po_get_domain(company_id, values, partner)
        if "move_dest_ids" in values:
            origin = values["move_dest_ids"].origin
            order_id = self.env["sale.order"].search([("name", "=", origin)])
            if order_id:
                values["group_id"] = False
                default_route_id = order_id.route_id
                if not default_route_id.split_purchase_by_route:
                    domain = tuple(filter(lambda r: r[0] != "group_id", domain))
                    domain += (
                        (
                            "default_route_id",
                            "=",
                            default_route_id.id,
                        ),
                    )
        return domain
