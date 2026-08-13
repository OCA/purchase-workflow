# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def _get_action_view_purchase_requests(self):
        """Window action showing exactly this set of requests."""
        action = {
            "name": _("Purchase Requests"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request",
            "context": {"create": False},
        }
        if len(self) == 1:
            action.update({"view_mode": "form", "res_id": self.id})
        else:
            action.update(
                {"view_mode": "tree,form", "domain": [("id", "in", self.ids)]}
            )
        return action
