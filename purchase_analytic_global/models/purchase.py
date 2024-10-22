# Copyright 2014-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "analytic.mixin"]

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        for rec in self:
            analytic = rec.mapped("order_line.analytic_distribution")
            analytic = list(filter(lambda x: x is not False, analytic))
            if len(analytic) > 1:
                analytic = [dict(t) for t in {tuple(d.items()) for d in analytic}]
            if len(analytic) == 1:
                rec.analytic_distribution = analytic and analytic[0] or False
            else:
                rec.analytic_distribution = False

    def _inverse_analytic_distribution(self):
        for rec in self:
            if rec.analytic_distribution:
                rec.order_line.analytic_distribution = rec.analytic_distribution
