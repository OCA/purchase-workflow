# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        """ """
        domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
        partner_id = values["move_dest_ids"].partner_id
        incoterm = (
            self.env["ir.config_parameter"].sudo().get_param("account_incoterm", False)
        )
        incoterm = tuple(item.strip() for item in incoterm.split(","))
        if partner_id.purchase_incoterm_id.code in incoterm:
            domain += (("incoterm_id", "=", partner_id.purchase_incoterm_id.id),)
        else:
            domain += (
                "|",
                ("incoterm_id.code", "not in", incoterm),
                ("incoterm_id", "=", False),
            )
        return domain
