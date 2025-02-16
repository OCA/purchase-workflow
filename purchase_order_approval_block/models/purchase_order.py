# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval_block_id = fields.Many2one(
        comodel_name="purchase.approval.block.reason",
        string="Approval Block Reason",
    )
    approval_blocked = fields.Boolean(
        compute="_compute_approval_blocked",
    )

    @api.depends("approval_block_id")
    def _compute_approval_blocked(self):
        for rec in self:
            rec.approval_blocked = rec.approval_block_id

    @api.model_create_multi
    def create(self, mvals):
        records = super(PurchaseOrder, self).create(mvals)
        for vals, po in zip(mvals, records):
            if "approval_block_id" in vals and vals["approval_block_id"]:
                po.message_post(
                    body=_(
                        'Order "%(order_name)s" blocked with reason "%(block_name)s"'
                    )
                    % {
                        "order_name": po.name,
                        "block_name": po.approval_block_id.name,
                    }
                )
        return records

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for po in self:
            if "approval_block_id" in vals and vals["approval_block_id"]:
                po.message_post(
                    body=_(
                        'Order "%(order_name)s" blocked with reason "%(block_name)s"'
                    )
                    % {
                        "order_name": po.name,
                        "block_name": po.approval_block_id.name,
                    }
                )
            elif "approval_block_id" in vals and not vals["approval_block_id"]:
                po.message_post(body=_('Order "%s" approval block released.') % po.name)
        return res

    def button_approve(self, force=False):
        for rec in self:
            if rec.approval_block_id:
                rec.button_release_approval_block()
        return super(PurchaseOrder, self).button_approve(force=force)

    def button_release_approval_block(self):
        for order in self:
            order.approval_block_id = False
        return True
