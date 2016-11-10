# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _, workflow
import openerp.addons.decimal_precision as dp


class PurchaseLineCancelQuantity(models.TransientModel):
    _name = 'purchase.order.line_cancel_quantity'

    line_ids = fields.One2many('purchase.order.line_cancel_quantity_line',
                               'wizard_id', string='Lines')

    @api.model
    def default_get(self, fields):
        ctx = self.env.context.copy()
        po_ids = ctx.get('active_ids', [])
        po_line_obj = self.env['purchase.order.line']
        lines = []
        for po_line in po_line_obj.browse(po_ids):
            max_quantity = po_line.product_qty - po_line.invoiced_qty -\
                po_line.cancelled_qty
            lines.append({
                'po_line_id': po_line.id,
                'product_qty': max_quantity,
                'price_unit': po_line.price_unit,
            })
        defaults = super(PurchaseLineCancelQuantity, self).default_get(fields)
        defaults['line_ids'] = lines
        return defaults

    @api.multi
    def cancel_quantity(self):
        self.ensure_one()
        for line in self.line_ids:
            if line.cancelled_qty > line.product_qty:
                raise exceptions.Warning(
                    _("""Quantity to cancel is greater
                    than available quantity"""))
            # To allow to add some quantity already cancelled
            if line.cancelled_qty < 0 and\
                    abs(line.cancelled_qty) > line.po_line_id.cancelled_qty:
                raise exceptions.Warning(
                    _("""Quantity to cancel is greater
                    than quantity already cancelled"""))
            line.po_line_id.cancelled_qty += line.cancelled_qty
            workflow.trg_write(self._uid, 'purchase.order',
                               line.po_line_id.order_id.id, self._cr)


class PurchaseLineCancelQuantityLine(models.TransientModel):
    _name = 'purchase.order.line_cancel_quantity_line'

    po_line_id = fields.Many2one('purchase.order.line', 'Purchase order line',
                                 readonly=True)
    product_qty = fields.Float(
        'Quantity', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True)
    price_unit = fields.Float(related='po_line_id.price_unit',
                              string='Unit Price', readonly=True)
    cancelled_qty = fields.Float(
        string='Quantity to cancel',
        digits=dp.get_precision('Product Unit of Measure'))
    wizard_id = fields.Many2one('purchase.order.line_cancel_quantity',
                                'Wizard')
