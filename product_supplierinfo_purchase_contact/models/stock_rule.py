# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        if values.get("supplier") and values["supplier"].purchase_partner_id:
            partner = values["supplier"].purchase_partner_id
        return super()._make_po_get_domain(company_id, values, partner)

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        if "supplier" in values and values["supplier"].purchase_partner_id:
            res["partner_id"] = values["supplier"].purchase_partner_id.id
        return res
