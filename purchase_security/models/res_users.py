# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    purchase_team_ids = fields.Many2many(
        comodel_name="purchase.team",
        relation="purchase_team_res_users_rel",
        column1="res_users_id",
        column2="purchase_team_id",
        string="Purchases Teams",
        check_company=True,
        copy=False,
        readonly=True,
    )
