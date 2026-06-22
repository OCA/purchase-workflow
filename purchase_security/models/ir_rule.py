# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, tools
from odoo.fields import Domain
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """Inject extra domain for restricting partners when the user
        has the group 'Purchase / User (own orders)."""
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        group1 = "purchase_security.group_purchase_own_orders"
        group2 = "purchase_security.group_purchase_group_orders"
        group3 = "purchase.group_purchase_manager"
        if model_name == "res.partner" and not self.env.su:
            if user.has_group(group1) and not user.has_group(group3):
                partner_domain = Domain.OR(
                    [
                        Domain("message_partner_ids", "in", user.partner_id.ids),
                        Domain("id", "=", user.partner_id.id),
                    ]
                )
                if user.has_group(group2):
                    extra_domain = Domain.OR(
                        [
                            partner_domain,
                            Domain(
                                "purchase_team_id", "=", user.purchase_team_ids[:1].id
                            ),
                            Domain("purchase_team_id", "=", False),
                        ]
                    )
                else:
                    extra_domain = Domain.OR(
                        [
                            partner_domain,
                            Domain("purchase_user_id", "=", user.id),
                            Domain.AND(
                                [
                                    Domain("purchase_user_id", "=", False),
                                    Domain.OR(
                                        [
                                            Domain("purchase_team_id", "=", False),
                                            Domain(
                                                "purchase_team_id",
                                                "=",
                                                user.purchase_team_ids[:1].id,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    )
                res = Domain.AND([extra_domain, Domain(res)])
        return res
