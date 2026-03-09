# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        if values.get("supplier"):
            purchase_partner = self._get_valid_purchase_partner(values["supplier"])
            if purchase_partner:
                partner = purchase_partner
        return super()._make_po_get_domain(company_id, values, partner)

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        if "supplier" in values:
            purchase_partner = self._get_valid_purchase_partner(values["supplier"])
            if purchase_partner:
                res["partner_id"] = purchase_partner.id
        return res

    def _get_valid_purchase_partner(self, supplier):
        today = fields.Date.today()
        valid = supplier.search(
            [
                ("partner_id", "=", supplier.partner_id.id),
                ("product_tmpl_id", "=", supplier.product_tmpl_id.id),
                ("purchase_partner_id", "!=", False),
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", today),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", today),
            ],
            order="date_start desc",
            limit=1,
        )
        return valid.purchase_partner_id if valid else supplier.purchase_partner_id
