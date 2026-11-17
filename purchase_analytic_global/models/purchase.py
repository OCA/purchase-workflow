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
        """If all order line have same analytic distribution set analytic_distribution.
        If no lines, respect value given by the user.
        """
        for rec in self:
            if rec.order_line:
                al = rec.order_line[0].analytic_distribution or False
                for ol in rec.order_line:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                rec.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        for rec in self:
            if rec.analytic_distribution:
                rec.order_line.write(
                    {"analytic_distribution": rec.analytic_distribution}
                )

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When change analytic_distribution set analytic distribution on all order lines"""
        if self.analytic_distribution:
            self.order_line.update(
                {"analytic_distribution": self.analytic_distribution}
            )
