# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#

from functools import partial
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _
from openerp.tools import html2plaintext, float_compare


class PurchaseOrderAmendment(models.TransientModel):
    _name = 'purchase.order.amendment'

    purchase_id = fields.Many2one(comodel_name='purchase.order',
                                  string='Purchase Order',
                                  required=True,
                                  readonly=True)
    item_ids = fields.One2many(comodel_name='purchase.order.amendment.item',
                               inverse_name='amendment_id',
                               string='Items')
    reason = fields.Html()

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrderAmendment, self).default_get(fields)
        purchase_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')

        if not purchase_ids or len(purchase_ids) != 1:
            return res
        assert active_model == 'purchase.order', 'Bad context propagation'

        purchase = self.env['purchase.order'].browse(purchase_ids)

        if (purchase.invoice_method != 'picking' and
                any(inv.state != 'cancel' for inv in purchase.invoice_ids)):
            raise exceptions.Warning(
                _('An invoiced order cannot be amended')
            )

        items = []
        for line in purchase.order_line:
            if line.state in ('cancel', 'done'):
                continue
            elif line.amended_by_ids:
                continue
            items.append(self._prepare_item(line))
        res['item_ids'] = items
        return res

    @api.model
    def _prepare_item(self, purchase_line):
        ordered = purchase_line.product_qty

        received = purchase_line.received_qty
        canceled = 0.
        for move in purchase_line.move_ids:
            if move.state == 'cancel':
                canceled += move.product_qty

        amend = ordered - canceled - received
        return {
            'purchase_line_id': purchase_line.id,
            'ordered_qty': purchase_line.product_qty,
            'received_qty': received,
            'canceled_qty': canceled,
            'amend_qty': amend,
        }

    @api.multi
    def _message_content(self):
        title = _('Order amendment')
        message = '<h3>%s</h3><ul>' % title
        for item in self.item_ids:
            cancel_qty = item.ordered_qty - item.received_qty - item.amend_qty
            message += _('<li><b>%s</b>: %s Ordered, %s '
                         'Received, %s Canceled, %s Remaining amended quantity</li>') \
                         % (item.purchase_line_id.name,
                            item.ordered_qty,
                            item.received_qty,
                            cancel_qty,
                            item.amend_qty,
                            )
        message += '</ul>'
        # if the html field is touched, it may return '<br/>' or
        # '<p></p>' so check if it contains text at all
        if self.reason and html2plaintext(self.reason).strip():
            title = _('Reason for amending')
            message += "<h3>%s</h3><p>%s</p>" % (title, self.reason)
        return message

    @api.multi
    def do_amendment(self):
        self.ensure_one()
        purchase = self.purchase_id
        purchase.message_post(body=self._message_content())
        self.item_ids.split_lines()
        return True

    @api.multi
    def wizard_view(self):
        view = self.env.ref('purchase_amendment.view_purchase_order_amendment')

        return {
            'name': _('Enter the amendment details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.amendment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }


class PurchaseOrderAmendmentItem(models.TransientModel):
    _name = 'purchase.order.amendment.item'

    amendment_id = fields.Many2one(comodel_name='purchase.order.amendment',
                                   string='Amendment',
                                   required=True,
                                   ondelete='cascade',
                                   readonly=True)
    purchase_line_id = fields.Many2one(comodel_name='purchase.order.line',
                                       string='Line',
                                       required=True,
                                       readonly=True)
    ordered_qty = fields.Float(string='Ordered',
                               digits_compute=dp.get_precision('Product UoS'),
                               readonly=True)
    received_qty = fields.Float(string='Received',
                                readonly=True,
                                digits_compute=dp.get_precision('Product UoS'))
    canceled_qty = fields.Float(string='Canceled Moves',
                                readonly=True,
                                digits_compute=dp.get_precision('Product UoS'))
    amend_qty = fields.Float(string='Amend',
                             digits_compute=dp.get_precision('Product UoS'))
    product_uom_id = fields.Many2one(related='purchase_line_id.product_uom',
                                     readonly=True)

    @api.multi
    def split_lines(self):
        """ Split the order line according to selected quantities

        The received quantity is the quantity that will remain in the original
        purchases order line.
        The canceled quantity will split the original line and cancel the
        duplicated line.
        The amended quantity will split the original line; the
        duplicated line will be 'confirmed' and a new picking will be created.
        """
        moves_to_cancel = self.env['stock.move'].browse()
        for item in self:
            line = item.purchase_line_id
            amend_qty = item.amend_qty
            received_qty = item.received_qty
            ordered_qty = item.ordered_qty
            rounding = line.product_id.uom_id.rounding
            # the total canceled may be different than the one displayed
            # to the user, because the one displayed is the quantity
            # canceled in the *pickings*, here it includes also the
            # quantity removed when amending
            compare = partial(float_compare, precision_digits=rounding)
            canceled_qty = ordered_qty - received_qty - amend_qty
            if compare(canceled_qty, 0) == -1:  # Means: canceled_qty < 0
                # The amendment is bigger than ordered qty
                # Cancel the ordered quantity, create a new line for the
                # amendment
                canceled_qty = ordered_qty - received_qty

            if (not (received_qty or canceled_qty) and
                    compare(amend_qty, ordered_qty) == 0):
                # Means: amend_qty == ordered_qty
                # the line is not changed
                continue

            if (not canceled_qty and
                    compare(received_qty + amend_qty, ordered_qty) == 0):
                # Means: received_qty + amend_qty == ordered_qty
                # part has been received but there is no reason to split
                # the lines
                continue

            procurements = line.procurement_ids
            moves = line.move_ids
            if received_qty:
                # leave the 'done' procurements on this line
                proc = procurements.filtered(lambda p: p.state == 'done')
                procurements -= proc
                # only keep the done moves on the purchase line
                move = moves.filtered(lambda p: p.state == 'done')
                moves -= move
                # update the current line with the received qty,
                # the rest will be either canceled either amended,
                # either both
                line.write({
                    'product_qty': received_qty,
                    'move_ids': [(6, 0, move.ids)],
                })

            # new moves will be generated for the new quantities
            moves.filtered(lambda m: m.state != 'done').action_cancel()

            if canceled_qty:
                # only keep the canceled procurement on the purchase line
                proc = procurements.filtered(lambda p: p.state == 'cancel')
                procurements -= proc
                # only keep the canceled moves on the purchase line
                values = {'product_qty': canceled_qty,
                          'move_ids': [(6, 0, moves.ids)],
                          'procurement_ids': [(6, 0, proc.ids)]}
                if received_qty:
                    values['amend_id'] = line.id
                    # current line kept for the received quantity so
                    # create a new one
                    canceled_line = line.copy(default=values)
                    proc.write({'purchase_line_id': canceled_line.id})
                else:
                    # cancel the current line
                    line.write(values)
                    canceled_line = line
                moves_to_cancel |= canceled_line.move_ids
                canceled_line.action_cancel()

            if amend_qty:
                # link the new line with the remaining procurements
                # (not done nor canceled)
                values = {'product_qty': amend_qty,
                          'amend_id': line.id,
                          'move_ids': False,
                          'procurement_ids': [(6, 0, procurements.ids)]}
                amend_line = line.copy(default=values)
                amend_line.action_confirm()
                # procurement not done nor canceled are linked with this
                # line
                procurements.write({'purchase_line_id': amend_line.id})

        self.picking_recreate()
        # they must be canceled after the creation of the new pickings
        # otherwise the order's state change to 'except_picking'
        moves_to_cancel.filtered(lambda mv: mv.state != 'done').action_cancel()
        return True

    @api.multi
    def picking_recreate(self):
        purchase = self.mapped('purchase_line_id.order_id')
        purchase_model = self.env['purchase.order']

        lines = self.env['purchase.order.line'].browse()
        for line in purchase.order_line:
            if line.state == 'cancel':
                continue
            elif line.received:
                continue
            # check if we already have moves before generating them
            rounding = line.product_uom.rounding
            if float_compare(line.product_qty, line.move_qty,
                             precision_digits=rounding) == 0:
                # when we have the same quantity of moves, we don't need
                # to create new ones
                continue
            lines += line

        if not lines:
            return

        for picking in purchase.picking_ids:
            if picking.state == 'assigned':
                # reuse existing picking
                purchase_model._create_stock_moves(purchase, lines, picking.id)
                break
        else:
            picking_vals = {
                'picking_type_id': purchase.picking_type_id.id,
                'partner_id': purchase.partner_id.id,
                'date': max([l.date_planned for l in purchase.order_line
                             if l.state != 'cancel']),
                'origin': purchase.name,
            }
            picking = self.env['stock.picking'].create(picking_vals)
            purchase_model._create_stock_moves(purchase, lines, picking.id)
        purchase.signal_workflow('picking_amend')
