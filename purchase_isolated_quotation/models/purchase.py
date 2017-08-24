# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_order = fields.Boolean(  # False is quotation, True is PO.
        string='Order type',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('is_order', False),
    )
    quote_id = fields.Many2one(
        'purchase.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Order Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    state2 = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Mail Sent'),
         ('cancel', 'Cancelled'),
         ('done', 'Done'), ],
        string='Status',
        readonly=True,
        related='state',
        help="A dummy state used for Quotation",
    )

    @api.model
    def create(self, vals):
        is_order = vals.get('is_order', False) or \
            self._context.get('is_order', False)
        if not is_order and vals.get('name', '/') == '/':
            Seq = self.env['ir.sequence']
            vals['name'] = Seq.next_by_code('purchase.quotation') or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def action_convert_to_order(self):
        self.ensure_one()
        if self.is_order:
            raise UserError(
                _('Only quotation can convert to order'))
        Seq = self.env['ir.sequence']
        order = self.copy({
            'name': Seq.next_by_code('purchase.order') or '/',
            'is_order': True,
            'quote_id': self.id,
            'partner_ref': self.partner_ref
        })
        self.order_id = order.id
        if self.state == 'draft':
            self.button_done()
        return self.open_purchase_order()

    @api.model
    def open_purchase_order(self):
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'purchase.order',
            'context': {'is_order': True, },
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('is_order', '=', 'True')]",
            'res_id': self.order_id and self.order_id.id or False,
        }
