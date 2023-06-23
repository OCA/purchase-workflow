# Copyright 2023 Tecnativa - Stefan Ungureanu
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseTeam(models.Model):
    _name = "purchase.team"
    _description = "Purchase Team"

    name = fields.Char()
    user_ids = fields.Many2many("res.users", string="Purchase Users")
