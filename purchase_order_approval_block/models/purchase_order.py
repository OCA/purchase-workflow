# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval_block_id = fields.Many2one(
        comodel_name='purchase.approval.block.reason',
        string='Approval Block Reason',
    )
    approval_blocked = fields.Boolean(
        'Approval Blocked',
        compute='_compute_approval_blocked',
    )

    @api.onchange('amount_untaxed')
    def onchange_amount_untaxed(self):
        approval_block_id = self.env['purchase.approval.block.reason'].search([
            ('amount', '<=', self.amount_untaxed)
        ], limit=1, order='amount desc')
        if approval_block_id:
            self.approval_block_id = approval_block_id.id
        else:
            self.approval_block_id = False

    def _compute_approval_blocked(self):
        for rec in self:
            if rec.approval_block_id:
                rec.approval_blocked = True
            else:
                rec.approval_blocked = False

    @api.model_create_multi
    def create(self, vals_list):
        po = super(PurchaseOrder, self).create(vals_list)
        for rec in po:
            if rec.approval_block_id:
                po.message_post(body=_('Order \"%s\" blocked with reason'
                                       ' \"%s\"') % (rec.name,
                                                     rec.approval_block_id.name))
        return po

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for po in self:
            if 'approval_block_id' in vals and vals['approval_block_id']:
                po.message_post(
                    body=_('Order \"%s\" blocked with reason \"%s\"') % (
                        po.name, po.approval_block_id.name))
            elif 'approval_block_id' in vals and not vals['approval_block_id']:
                po.message_post(
                    body=_('Order \"%s\" approval block released.') % po.name)
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
