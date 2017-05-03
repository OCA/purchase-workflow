# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Ecosoft (<http://www.ecosoft.co.th>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Selection(
        [('quotation', 'Quotation'),
         ('purchase_order', 'Purchase Order'), ],
        string='Order Type',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('order_type', 'quotation'),
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
    invoice_method = fields.Selection(
        [('manual', 'Based on Purchase Order lines'),
         ('order', 'Based on generated draft invoice'),
         ('picking', 'Based on incoming shipments'), ]
    )

    @api.model
    def create(self, vals):
        if (vals.get('order_type', False) or
            self._context.get('order_type', 'quotation')) == 'quotation' \
                and vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('purchase.quotation') or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def action_button_convert_to_order(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        order = self.copy({
            'name': self.env['ir.sequence'].get('purchase.order') or '/',
            'order_type': 'purchase_order',
            'quote_id': self.id,
            'partner_ref': self.partner_ref
        })
        self.order_id = order.id
        if self.state == 'draft':
            self.button_done()
        return self.open_purchase_order()

    def open_purchase_order(self):
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'purchase.order',
            'context': { 'order_type': 'purchase_order', },
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'domain': "[('order_type', '=', 'purchase_order')]",
            'res_id': self.order_id and self.order_id.id or False,
        }
