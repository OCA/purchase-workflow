# Copyright 2023 Tecnativa - Stefan Ungureanu
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    team_id = fields.Many2one(
        "purchase.team",
        string="Team",
        index=True,
        auto_join=True,
    )
