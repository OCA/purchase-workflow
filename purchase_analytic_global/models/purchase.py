# Copyright 2014-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        store=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="This analytic distribution will be propagated to all lines, if you need "
        "to use different analytics, define the account at line level.",
    )

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        """Set the analytic distribution on the order based on its order lines.

        If all order lines have the same analytic distribution,
        then set it on the order, otherwise left the field empty.
        """
        res = super()._compute_analytic_distribution()
        for order in self:
            distributions = order.mapped("order_line.analytic_distribution")
            if distributions and all(
                distribute == distributions[0] for distribute in distributions
            ):
                order.analytic_distribution = distributions[0]
            else:
                order.analytic_distribution = False
        return res

    def _inverse_analytic_distribution(self):
        for rec in self:
            if rec.analytic_distribution:
                rec.order_line.write(
                    {"analytic_distribution": rec.analytic_distribution}
                )
