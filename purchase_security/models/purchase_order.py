# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_user_id_editable = fields.Boolean(
        compute="_compute_is_user_id_editable",
    )
    team_id = fields.Many2one(
        "purchase.team",
        string="Team",
        index=True,
        auto_join=True,
        compute="_compute_team_id",
        store=True,
        readonly=False,
    )

    def _compute_is_user_id_editable(self):
        is_user_id_editable = self.env.user.has_group(
            "purchase.group_purchase_manager"
        ) or not self.env.user.has_group("purchase_security.group_purchase_own_orders")
        self.write({"is_user_id_editable": is_user_id_editable})

    @api.depends("user_id")
    def _compute_team_id(self):
        """When a user is assigned, the first team which the user belongs to is
        assigned, and if no one, the first purchase team.
        """
        first_team = self.env["purchase.team"].search([], limit=1)
        for record in self:
            if record.user_id:
                team = self.env["purchase.team"].search(
                    [("user_ids", "=", record.user_id.id)], limit=1
                )
                if team:
                    record.team_id = team.id
                    continue
            record.team_id = first_team.id
