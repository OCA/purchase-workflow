# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        ondelete="restrict",
        string="Default Purchase Incoterm",
    )
    purchase_incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="restrict",
        string="Default Purchase Incoterm Address",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            "purchase_incoterm_address_id",
            "purchase_incoterm_id",
        ]
