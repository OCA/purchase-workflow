# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_currency_id = fields.Many2one(
        string="Purchase currency", related="purchase_id.currency_id", readonly=True,
    )
    show_currency_rate_amount = fields.Boolean(
        compute="_compute_show_currency_rate_amount", readonly=True
    )
    currency_rate_amount = fields.Float(
        string="Rate amount", compute="_compute_currency_rate_amount", digits=0,
    )

    @api.depends("purchase_currency_id", "purchase_currency_id.rate_ids", "company_id")
    def _compute_show_currency_rate_amount(self):
        for item in self:
            item.show_currency_rate_amount = (
                item.purchase_id.currency_id
                and item.purchase_id.currency_id != item.company_id.currency_id
            )

    @api.depends("purchase_currency_id", "show_currency_rate_amount", "company_id")
    def _compute_currency_rate_amount(self):
        self.currency_rate_amount = 1
        for item in self.filtered("show_currency_rate_amount"):
            rates = item.purchase_currency_id._get_rates(
                item.company_id, fields.Date.context_today(self)
            )
            item.currency_rate_amount = rates.get(item.purchase_currency_id.id)
