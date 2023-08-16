# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[("approved", "Approved"), ("purchase",)])

    READONLY_STATES = {
        "purchase": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
        "approved": [("readonly", True)],
    }

    # Update the readonly states:
    origin = fields.Char(states=READONLY_STATES)
    date_order = fields.Datetime(states=READONLY_STATES)
    partner_id = fields.Many2one(states=READONLY_STATES)
    dest_address_id = fields.Many2one(states=READONLY_STATES)
    currency_id = fields.Many2one(states=READONLY_STATES)
    order_line = fields.One2many(states=READONLY_STATES)
    company_id = fields.Many2one(states=READONLY_STATES)
    picking_type_id = fields.Many2one(states=READONLY_STATES)

    def button_release(self):
        return super(PurchaseOrder, self).button_approve()

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
