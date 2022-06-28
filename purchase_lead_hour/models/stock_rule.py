# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_lead_days(self, product):
        delay, description = super()._get_lead_days(product)
        delay_hour = self._get_seller_lead_hours(product)
        delay += delay_hour / 24
        return delay, description

    def _get_seller_lead_hours(self, product):
        """Returns the main's seller delay_hour"""
        buy_rule = self.filtered(lambda r: r.action == "buy")
        seller = product.with_company(buy_rule.company_id)._select_seller(quantity=None)
        if not buy_rule or not seller:
            return 0.0
        buy_rule.ensure_one()
        return seller[0].delay_hour
