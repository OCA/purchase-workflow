# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PurchaseCostDistribution(models.Model):
    _inherit = "purchase.cost.distribution"

    total_volumetric_weight = fields.Float(
        compute="_compute_total_volumetric_weight",
        string="Total volumetric weight",
        readonly=True,
        digits="Stock Weight",
    )

    @api.depends("cost_lines", "cost_lines.total_volumetric_weight")
    def _compute_total_volumetric_weight(self):
        for distribution in self:
            distribution.total_volumetric_weight = sum(
                [x.total_volumetric_weight for x in distribution.cost_lines]
            )

    @api.model
    def _prepare_expense_line_volumetric_weight(self, expense_line, cost_line):
        multiplier = cost_line.total_volume
        if expense_line.affected_lines:
            divisor = sum([x.total_volume for x in expense_line.affected_lines])
        else:
            divisor = cost_line.distribution.total_volume
        return multiplier, divisor


class PurchaseCostDistributionLine(models.Model):
    _inherit = "purchase.cost.distribution.line"

    product_volumetric_weight = fields.Float(
        string="Volumetric weight",
        related="product_id.product_tmpl_id.volumetric_weight",
        digits="Stock Weight",
    )
    total_volumetric_weight = fields.Float(
        compute="_compute_total_volumetric_weight",
        string="Line volumetric weight",
        store=True,
        digits="Stock Weight",
    )

    @api.depends("product_id", "product_qty")
    def _compute_total_volumetric_weight(self):
        for dist_line in self:
            dist_line.total_volumetric_weight = (
                dist_line.product_volumetric_weight * dist_line.product_qty
            )
