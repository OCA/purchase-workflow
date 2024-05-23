# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
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
            record.team_id = record.user_id.purchase_team_ids[:1] or first_team

    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            partner = self.partner_id.commercial_partner_id
            if not self.env.context.get("default_user_id"):
                self.user_id = partner.purchase_user_id or self.env.user
            if not self.env.context.get("default_team_id"):
                self.team_id = (
                    partner.purchase_team_id
                    or self.user_id.purchase_team_ids[:1]
                    or self.env["purchase.team"].search([], limit=1)
                )
        return res
