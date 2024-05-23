# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseTeam(models.Model):
    _name = "purchase.team"
    _description = "Purchase Team"
    _order = "sequence,id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="purchase_team_res_users_rel",
        column1="purchase_team_id",
        column2="res_users_id",
        string="Purchase Users",
    )
