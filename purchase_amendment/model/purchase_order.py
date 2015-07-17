# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier, Jordi Ballester Alomar
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
from openerp.osv import fields, orm


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def button_amend(self, cr, uid, ids, context=None):
        if ids:
            po_id = ids[0]
        else:
            return False
        amend_model = self.pool['purchase.order.amendment']
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': ids[0],
        })
        amendment = amend_model.create(cr, uid, {'purchase_id': po_id},
                                       context=context)
        return amend_model.wizard_view(cr, uid, amendment, context=context)

    def action_picking_create(self, cr, uid, ids, context=None):
        for purchase in self.browse(cr, uid, ids, context=context):
            # since we added a transition from picking_except to
            # picking, we prevent the picking to be created again
            if purchase.picking_ids:
                # change from picking_except to confirmed
                self.write(cr, uid, purchase.id, {'state': 'approved'},
                           context=context)
                continue
        return super(PurchaseOrder, self).action_picking_create(
            cr, uid, ids, context=context)

    def canceled_picking_not_canceled_line(self, cr, uid, ids, *args):
        for purchase in self.browse(cr, uid, ids):
            for line in purchase.order_line:
                if line.state == 'cancel':
                    continue
                for move in line.move_ids:
                    if move.state == 'cancel':
                        return True
        return False


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'amend_id': fields.many2one('purchase.order.line', 'Amend Line'),
        'amended_by_ids': fields.one2many('purchase.order.line',
                                          'amend_id', 'Amended by lines')
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'amend_id': False,
        })
        return super(PurchaseOrderLine, self).copy(cr, uid, id, default,
                                                   context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        # We will group by PO first, so we do the check only once for each PO
        purchase_orders = list(set([x.order_id for x in self.browse(
            cr, uid, ids, context=context)]))
        for purchase in purchase_orders:
            if all([l.state == 'cancel' for l in purchase.order_line]):
                self.pool.get('purchase.order').action_cancel(
                    cr, uid, [purchase.id], context=context)
        return True
