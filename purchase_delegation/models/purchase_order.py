# Copyright 2022 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    validator_id = fields.Many2one(
        "res.users", "Validated by (délégation)", readonly=True, tracking=True
    )

    def button_approve_as(self):
        for po in self.filtered(lambda order: order.state == "to approve"):
            for delegator_id in self.env["delegation"].get_delegators(
                delegate_id=self.env.user.id, model=self._name
            ):
                if (
                    self.with_user(delegator_id).user_has_groups(
                        "purchase.group_purchase_manager"
                    )
                    and po.with_user(delegator_id)._approval_allowed()
                ):
                    po.with_user(delegator_id).write(
                        {
                            "state": "approved",
                            "validator_id": self.env.user.id,
                        }
                    )
                    break
        return {}

    def button_release(self):
        self.write({"state": "purchase", "date_approve": fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == "lock").write({"state": "done"})
        return {}
