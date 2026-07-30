# Copyright 2023 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        supplier = values.get("supplier")
        if supplier and supplier.currency_id:
            domain += (("currency_id", "=", supplier.currency_id.id),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        seller = values.get("supplier")
        seller_currency_id = seller.currency_id.id
        company_currency_id = self.env.user.company_id.currency_id.id
        res["currency_id"] = seller_currency_id or company_currency_id
        return res
