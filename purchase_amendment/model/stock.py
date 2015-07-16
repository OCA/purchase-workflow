# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""
from openerp.osv import orm
from openerp.tools.translate import _


class stock_move(orm.Model):

    _inherit = 'stock.move'

    def split(self, cr, uid, move, qty, context=None):
        """ Splits qty from move move into a new move
        :param move: browse record
        :param qty: float. quantity to split (given in product UoM)
        returns the ID of the backorder move created
        """
        if move.state in ('done', 'cancel'):
            raise orm.except_orm(_('Error'),
                                 _('You cannot split a move done'))
        if move.state == 'draft':
            # we restrict the split of a draft move because if not confirmed
            # yet, it may be replaced by several other moves in
            # case of phantom bom (with mrp module).
            # And we don't want to deal with this complexity by
            # copying the product that will explode.
            raise orm.except_orm(_('Error'),
                                 _('You cannot split a draft move. '
                                   'It needs to be confirmed first.'))

        if move.product_qty <= qty or qty == 0:
            return move.id

        uom_obj = self.pool.get('product.uom')
        context = context or {}

        # HALF-UP rounding as only rounding errors will be because of
        # propagation of error from default UoM
        uom_qty = uom_obj._compute_qty_obj(
            cr, uid, move.product_id.uom_id, qty, move.product_uom,
            context=context)
        uos_qty = uom_qty * move.product_uos_qty / move.product_qty

        defaults = {
            'product_qty': uom_qty,
            'product_uos_qty': uos_qty,
            'move_dest_id': move.move_dest_id.id,
        }
        new_move = self.copy(cr, uid, move.id, defaults, context=context)

        ctx = context.copy()
        ctx['do_not_propagate'] = True
        self.write(cr, uid, [move.id], {
            'product_qty': move.product_qty - uom_qty,
            'product_uos_qty': move.product_uos_qty - uos_qty,
        }, context=ctx)

        if move.move_dest_id and move.move_dest_id.state not in ('done',
                                                                 'cancel'):
            new_move_prop = self.split(cr, uid, move.move_dest_id, qty,
                                       context=context)
            self.write(cr, uid, [new_move], {'move_dest_id': new_move_prop},
                       context=context)
        # returning the first element of list returned by action_confirm is
        # ok because we checked it wouldn't be exploded (and
        # thus the result of action_confirm should always be a list of 1
        # element length)
        self.action_confirm(cr, uid, [new_move], context=context)
        return new_move
