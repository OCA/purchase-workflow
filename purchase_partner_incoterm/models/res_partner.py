# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        ondelete="restrict",
        string="Default Purchase Incoterm",
    )
