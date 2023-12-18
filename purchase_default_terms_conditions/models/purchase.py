# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        if self.partner_id.purchase_note:
            self.notes = self.partner_id.purchase_note
        elif (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase.use_purchase_note")
        ):
            self.notes = self.company_id.purchase_note
        return super().onchange_partner_id()

    @api.model
    def create(self, vals):
        order = super().create(vals)

        if order.notes:
            return order
        elif order.partner_id.purchase_note:
            order.notes = order.partner_id.purchase_note
        elif (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase.use_purchase_note")
        ):
            order.notes = order.company_id.purchase_note

        return order
