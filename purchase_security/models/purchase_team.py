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

    def open_form_view(self):
        """Allow to open the form view from the editable tree view.

        The main reason to use the form view is to manage the team members
        of larger teams. The many2many_avatar_user widget in the tree view
        does not allow to remove some of the users if ellipsis ('+3') is
        triggered in the widget.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase_security.action_purchase_team_display"
        )
        action.update(
            {
                "res_id": self.id,
                "view_mode": "form",
                "views": [(False, "form")],
            }
        )
        return action
