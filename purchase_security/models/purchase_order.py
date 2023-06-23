# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# Copyright 2023 Tecnativa - Stefan Ungureanu
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


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
    )

    def _compute_is_user_id_editable(self):
        is_user_id_editable = self.env.user.has_group(
            "purchase.group_purchase_manager"
        ) or not self.env.user.has_group("purchase_security.group_purchase_own_orders")
        self.write({"is_user_id_editable": is_user_id_editable})
