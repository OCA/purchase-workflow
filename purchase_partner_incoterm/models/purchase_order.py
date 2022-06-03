# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Incoterm Address",
        help="Address where goods responsibility is transferred to the buyer",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.incoterm_id = self.partner_id.purchase_incoterm_id
        self.incoterm_address_id = self.partner_id.purchase_incoterm_address_id
        return res
