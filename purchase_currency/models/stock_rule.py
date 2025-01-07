# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        result = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        partner = values["supplier"].partner_id
        supplier_currency = partner.with_company(
            company_id
        ).property_purchase_currency_id
        default_purchase_currency = self.env.company.default_purchase_currency_id
        if not supplier_currency and default_purchase_currency:
            result.update(currency_id=default_purchase_currency.id)
        return result
