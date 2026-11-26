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

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        use_purchase_note = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase.use_purchase_note")
        )
        for order in orders:
            # Orders created programmatically (e.g. by procurement/MTO rules)
            # never trigger the UI onchange above, so notes stays blank.
            # Backfill it here the same way, without overwriting a value
            # the caller explicitly provided.
            if order.notes:
                continue
            if order.partner_id and not is_html_empty(order.partner_id.purchase_note):
                order.notes = order.partner_id.purchase_note
            elif use_purchase_note and str2bool(use_purchase_note):
                order.notes = order.company_id.purchase_note
        return orders
