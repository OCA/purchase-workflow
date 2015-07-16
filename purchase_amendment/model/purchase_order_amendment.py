# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier, Leonardo Pistone, Jordi Ballester Alomar
#    Copyright 2015 Camptocamp SA
#    Copyright 2015 Eficent
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
from openerp.osv import fields, orm
from openerp.tools import html2plaintext, float_compare
from openerp.tools.translate import _


class PurchaseOrderAmendment(orm.TransientModel):
    _name = 'purchase.order.amendment'

    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',
                                       required=True, readonly=True),
        'item_ids': fields.one2many('purchase.order.amendment.item',
                                    'amendment_id', 'Items'),
        'reason': fields.html()
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(PurchaseOrderAmendment, self).default_get(
            cr, uid, fields, context=context)
        purchase_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not purchase_ids or len(purchase_ids) != 1:
            return res
        assert active_model == 'purchase.order', 'Bad context propagation'

        purchase = self.pool['purchase.order'].browse(cr, uid, purchase_ids[0],
                                                      context=context)

        if (purchase.invoice_method != 'picking' and
                any(inv.state != 'cancel' for inv in purchase.invoice_ids)):
            raise orm.except_orm(
                _('Error!'),
                _("An invoiced order cannot be amended"))

        items = []
        for purchase_line in purchase.order_line:
            if purchase_line.state == 'cancel':
                continue
            for move in purchase_line.move_ids:
                if move.state == 'cancel':
                    continue
                items += self._prepare_move_item(cr, uid, move,
                                                 context=context)
        res['item_ids'] = items
        return res

    def _prepare_move_item(self, cr, uid, move, context=None):
        return [{
            'purchase_line_id': move.purchase_line_id.id,
            'move_id': move.id,
            'original_qty': move.product_qty,
            'new_qty': move.product_qty,
            'state': move.state,
            'origin': move.name or '',
        }]

    def _message_content(self, cr, uid, poa_id, context=None):
        title = _('Order amendment')
        message = '<h3>%s</h3><ul>' % title
        poa = self.browse(cr, uid, poa_id, context=context)
        for item in poa.item_ids:
            message += _(
                '<li><b>%s</b>: Origin %s, Original quantity %s, '
                'New quantity %s, State %s</li>'
            ) % (item.purchase_line_id.name,
                 item.origin,
                 item.original_qty,
                 item.new_qty,
                 item.state,
                 )
        message += '</ul>'
        # if the html field is touched, it may return '<br/>' or
        # '<p></p>' so check if it contains text at all
        if poa.reason and html2plaintext(poa.reason).strip():
            title = _('Reason for amending')
            message += "<h3>%s</h3><p>%s</p>" % (title, poa.reason)
        return message

    def do_amendment(self, cr, uid, ids, context=None):
        purchase_obj = self.pool['purchase.order']
        po_amend_item_obj = self.pool['purchase.order.amendment.item']
        for poa in self.browse(cr, uid, ids, context=context):
            purchase = poa.purchase_id
            message = self._message_content(cr, uid, poa.id, context=context)
            purchase_obj.message_post(cr, uid, [purchase.id], body=message)
            poa_item_ids = [item.id for item in poa.item_ids]
            po_amend_item_obj.split_lines(cr, uid, poa_item_ids,
                                          context=context)
            return True

    def wizard_view(self, cr, uid, id, context=None):
        mod_obj = self.pool.get('ir.model.data')
        get_ref = mod_obj.get_object_reference
        __, view_id = get_ref(cr, uid, 'purchase_amendment',
                              'view_purchase_order_amendment')

        return {
            'name': _('Enter the amendment details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.amendment',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': id,
            'context': context,
        }


class PurchaseOrderAmendmentItem(orm.TransientModel):
    _name = 'purchase.order.amendment.item'

    _columns = {
        'amendment_id': fields.many2one('purchase.order.amendment',
                                        'Amendment',
                                        required=True,
                                        ondelete='cascade',
                                        readonly=True),
        'purchase_line_id': fields.many2one('purchase.order.line',
                                            'Line',
                                            required=True,
                                            readonly=True),
        'origin': fields.char(readonly=True),
        'move_id': fields.many2one('stock.move',
                                   readonly=True),
        'original_qty': fields.float(string='Ordered',
                                     digits_compute=dp.get_precision(
                                         'Product UoS'),
                                     readonly=True),
        'new_qty': fields.float(string='Amend',
                                digits_compute=dp.get_precision('Product '
                                                                'UoS')),
        'state': fields.char(readonly=True),
        'product_id': fields.related('purchase_line_id',
                                     'product_id', type='many2one',
                                     relation='product.product',
                                     readonly=True),
        'product_uom_id': fields.related('purchase_line_id',
                                         'product_uom', type='many2one',
                                         relation='product.uom',
                                         readonly=True)
    }

    def _split_lines_hook(self, cr, uid, item_id, context=None):
        return True

    def split_lines(self, cr, uid, ids, context=None):
        """ Split the order line according to selected quantities

        The received quantity is the quantity that will remain in the original
        purchases order line.
        The canceled quantity will split the original line and cancel the
        duplicated line.
        The amended quantity will split the original line; the
        duplicated line will be 'confirmed' and a new picking will be created.
        """
        move_obj = self.pool['stock.move']
        po_line_obj = self.pool['purchase.order.line']
        for item in self.browse(cr, uid, ids, context=context):
            line = item.purchase_line_id
            rounding = line.product_id.uom_id.rounding
            compare = partial(float_compare, precision_digits=rounding)

            if compare(item.original_qty, item.new_qty) == 0:  # no changes
                continue
            elif compare(item.new_qty, 0.) == 0:  # new quantity is zero
                if compare(item.original_qty,
                           line.product_qty) == 0:
                    # this purchase line has only one move, and quantity goes
                    # to zero: cancel the move and the purchase order line
                    move_obj.action_cancel(cr, uid, [item.move_id.id],
                                           context=context)
                    po_line_obj.action_cancel(cr, uid, [line.id],
                                              context=context)
                else:
                    # we cancel the move, but the purchase order line has some
                    # quantity left from other moves
                    values = {'product_qty': item.move_id.product_qty,
                              'amend_id': line.id}
                    cancel_line_id = po_line_obj.copy(cr, uid, line.id,
                                                      default=values)
                    cancel_line = po_line_obj.browse(cr, uid,
                                                     cancel_line_id,
                                                     context=context)
                    po_line_obj.action_cancel(cr, uid, [cancel_line_id],
                                              context=context)
                    new_qty = line.product_qty - cancel_line.product_qty
                    po_line_obj.write(cr, uid, [line.id],
                                      {'product_qty': new_qty},
                                      context=context)
                    move_obj.action_cancel(cr, uid, [item.move_id.id],
                                           context=context)

            elif compare(item.original_qty, item.new_qty) == 1:
                # quantity decreased
                canceled_qty = item.original_qty - item.new_qty
                split_move_id = move_obj.split(cr, uid, item.move_id,
                                               canceled_qty, context=context)
                canceled_move = move_obj.browse(cr, uid, split_move_id,
                                                context=context)
                values = {'product_qty': canceled_qty,
                          'amend_id': line.id}
                cancel_line = po_line_obj.copy(cr, uid, line.id,
                                               default=values)
                move_obj.write(cr, uid, [canceled_move.id],
                               {'purchase_line_id': cancel_line},
                               context=context)
                po_line_obj.action_cancel(cr, uid, [cancel_line],
                                          context=context)
                move_obj.action_cancel(cr, uid,
                                       [canceled_move.id],
                                       context=context)
                new_qty = line.product_qty - canceled_qty
                po_line_obj.write(cr, uid, [line.id],
                                  {'product_qty': new_qty},
                                  context=context)

            else:  # quantity increased
                # this should propagate to chained moves just fine
                move_obj.write(cr, uid, [item.move_id.id],
                               {'product_qty': item.new_qty,
                                'product_uos_qty': item.new_qty},
                               context=context)
                added_qty = item.new_qty - item.original_qty
                new_qty = item.purchase_line_id.product_qty + added_qty
                po_line_obj.write(cr, uid, [item.purchase_line_id.id],
                                  {'product_qty': new_qty},
                                  context=context)
            # We add a hook to allow for additional logic
            self._split_lines_hook(cr, uid, item.id, context=context)
        return True
