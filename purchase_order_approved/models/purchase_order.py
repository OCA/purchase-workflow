# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('approved', 'Approved')])
    # TODO: inhterit state but adding approved state in a position after 'to
    # aprove' state.

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
        'approved': [('readonly', True)],
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

    @api.multi
    def button_release(self):
        super(PurchaseOrder, self).button_approve()

    @api.multi
    def button_approve(self, force=False):
        approve_purchases = self.filtered(
            lambda p: p.company_id.purchase_approve_active)
        approve_purchases.write({'state': 'approved'})
        return super(PurchaseOrder, self - approve_purchases).button_approve(
            force=force)
