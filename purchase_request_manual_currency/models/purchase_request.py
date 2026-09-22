# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    manual_currency = fields.Boolean()
    type_currency = fields.Selection(
        selection=lambda self: self._get_label_currency_name(),
        default=lambda self: self._get_label_currency_name()[0][0],
    )

    def _get_label_currency_name(self):
        """Get label related currency"""
        names = {
            "company_currency_name": (
                self.env["res.company"].browse(self._context.get("company_id"))
                or self.env.company
            ).currency_id.name,
            "rate_currency_name": "Unit",
        }
        return [
            [
                "company_rate",
                self.env._(
                    "%(rate_currency_name)s per %(company_currency_name)s", **names
                ),
            ],
            [
                "inverse_company_rate",
                self.env._(
                    "%(company_currency_name)s per %(rate_currency_name)s", **names
                ),
            ],
        ]

    @api.depends(
        "currency_id", "date_start", "company_id", "manual_currency", "type_currency"
    )
    def _compute_currency_rate(self):
        res = super()._compute_currency_rate()
        for order in self:
            if order.manual_currency and order.type_currency == "inverse_company_rate":
                order.currency_rate = 1.0 / order.currency_rate
        return res

    @api.depends("estimated_cost", "currency_rate", "type_currency", "manual_currency")
    def _compute_estimated_cost_currency_company(self):
        res = super()._compute_estimated_cost_currency_company()
        for rec in self:
            if rec.manual_currency and rec.type_currency == "inverse_company_rate":
                rec.estimated_cost_cc = rec.estimated_cost * rec.currency_rate
        return res

    def action_refresh_currency(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(self.env._("Rate currency can refresh state draft only."))
        return self._compute_currency_rate()
