# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_user_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('share', '=', False)]",
        string="Purchase representative",
        index=True,
    )
    purchase_team_id = fields.Many2one(
        comodel_name="purchase.team",
        string="Purchase team",
        index=True,
    )
