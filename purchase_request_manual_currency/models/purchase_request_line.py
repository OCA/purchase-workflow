# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="request_id.company_currency_id",
        string="Company Currency",
    )
    estimated_cost_company_currency = fields.Monetary(
        string="Estimated Cost (Company Currency)",
        compute="_compute_amount_company_currency",
        store=True,
        currency_field="company_currency_id",
    )

    @api.depends(
        "estimated_cost",
        "request_id.manual_currency_rate",
        "request_id.type_currency",
        "request_id.manual_currency",
    )
    def _compute_amount_company_currency(self):
        for rec in self:
            rec.estimated_cost_company_currency = rec.estimated_cost
            # check multi-currency
            if rec.company_currency_id != rec.currency_id:
                # check manual currency
                if rec.request_id.manual_currency:
                    rate = (
                        rec.request_id.manual_currency_rate
                        if rec.request_id.type_currency == "inverse_company_rate"
                        else (1.0 / rec.request_id.manual_currency_rate)
                    )
                    rec.estimated_cost_company_currency = rec.estimated_cost * rate
                # default rate currency
                else:
                    rec.estimated_cost_company_currency = rec.currency_id._convert(
                        rec.estimated_cost,
                        rec.company_currency_id,
                        rec.company_id,
                        fields.Date.today(),
                    )
