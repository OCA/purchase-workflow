# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    manual_currency = fields.Boolean(
        string="Is Manual Currency",
    )
    manual_currency_id = fields.Many2one(
        string="Manual Currency",
        comodel_name="res.currency",
    )
    is_manual = fields.Boolean(compute="_compute_currency")
    custom_rate = fields.Float(
        digits="Purchase Currency",
        tracking=True,
        help="Set new currency rate to apply on the purchase request.",
    )
    manual_currency_cost = fields.Monetary(
        string="Estimated Cost (by currency)",
        currency_field="manual_currency_id",
    )

    @api.depends("manual_currency_id", "custom_rate", "manual_currency_cost")
    def _compute_currency(self):
        for rec in self:
            rec.is_manual = (
                rec.manual_currency_id and rec.currency_id != rec.manual_currency_id
            )
            if rec.is_manual and rec.custom_rate:
                rec.estimated_cost = rec.manual_currency_cost / rec.custom_rate
            else:
                rec.estimated_cost = rec.estimated_cost

    @api.onchange("manual_currency_id", "date_required")
    def _onchange_currency_change_rate(self):
        today = fields.Date.today()
        ctx = {"company_id": self.company_id.id, "date": self.date_required or today}
        if self.manual_currency_id:
            self.custom_rate = self.currency_id.with_context(
                **ctx
            )._get_conversion_rate(
                self.currency_id,
                self.manual_currency_id,
                self.company_id,
                self.date_required or today,
            )
