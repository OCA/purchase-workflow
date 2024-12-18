# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import is_html_empty, str2bool


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        use_purchase_note = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase.use_purchase_note")
        )
        if self.partner_id and not is_html_empty(self.partner_id.purchase_note):
            self.notes = self.partner_id.purchase_note
        elif use_purchase_note and str2bool(use_purchase_note):
            self.notes = self.company_id.purchase_note
        return super().onchange_partner_id()
