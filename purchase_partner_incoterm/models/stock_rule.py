# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        partner = self.env["res.partner"].browse(vals["partner_id"])
        if not partner:
            return vals
        commercial_partner = partner.commercial_partner_id
        vals["incoterm_id"] = commercial_partner.purchase_incoterm_id.id
        vals["incoterm_address_id"] = commercial_partner.purchase_incoterm_address_id.id
        vals["incoterm_location"] = commercial_partner.purchase_incoterm_location
        return vals
