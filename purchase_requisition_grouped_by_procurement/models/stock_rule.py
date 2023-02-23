# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_buy(self, procurements):
        _self = self.with_context(grouped_by_procurement=True)
        return super(StockRule, _self)._run_buy(procurements=procurements)
