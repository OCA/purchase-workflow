# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[("approved", "Approved"), ("purchase",)])

    def button_release(self):
        return super().button_approve()

    def button_approve(self, force=False):
        two_steps_purchase_approval_ids = []
        for rec in self:
            partner_requires_approve = (
                rec.partner_id.purchase_requires_second_approval == "always"
            )
            company_requires_approve = (
                rec.partner_id.purchase_requires_second_approval == "based_on_company"
                and rec.company_id.purchase_approve_active
            )
            if rec.state != "approved" and (
                partner_requires_approve or company_requires_approve
            ):
                two_steps_purchase_approval_ids.append(rec.id)
        two_steps_purchase_approval = self.browse(two_steps_purchase_approval_ids)
        two_steps_purchase_approval.write({"state": "approved"})
        one_step_purchase_approval = self - two_steps_purchase_approval
        return super(PurchaseOrder, one_step_purchase_approval).button_approve(
            force=force
        )
