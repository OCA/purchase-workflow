# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

import time
from openerp.osv import fields, orm
from openerp.tools.translate import _


class purchase_order(orm.Model):
    _inherit = 'purchase.order'
    _columns = {
        'carrier_id': fields.many2one("delivery.carrier", "Delivery Method",
                                      help="Complete this field if you plan "
                                           "to invoice the shipping based on "
                                           "picking."),
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        result = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, part)
        if part:
            dtype = self.pool.get('res.partner').browse(
                cr, uid, part).property_delivery_carrier.id
            result['value']['carrier_id'] = dtype
        return result

    def _prepare_order_picking(self, cr, uid, order, context=None):
        result = super(purchase_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        result.update(carrier_id=order.carrier_id.id)
        return result

    def delivery_set(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('purchase.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        acc_fp_obj = self.pool.get('account.fiscal.position')
        for order in self.browse(cr, uid, ids, context=context):
            src_address_id = order.partner_id
            dest_address_id = order.dest_address_id or False
            if (
                not dest_address_id
                and order.warehouse_id
                and order.warehouse_id.partner_id
            ):
                dest_address_id = order.warehouse_id.partner_id
            if not dest_address_id:
                raise orm.except_orm(_('No destination address available!'),
                                     _('An address must be added to the'
                                       'purchase order or the warehouse.'))
            grid_id = carrier_obj.grid_src_dest_get(cr, uid,
                                                    [order.carrier_id.id],
                                                    src_address_id.id,
                                                    dest_address_id.id)
            if not grid_id:
                raise orm.except_orm(_('No Grid Available!'),
                                     _('No grid matching for this carrier!'))

            if order.state not in ('draft', 'sent'):
                raise orm.except_orm(_('Order not in Draft State!'),
                                     _('The order state have to be draft '
                                       'to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)

            taxes = grid.carrier_id.product_id.taxes_id
            fpos = order.fiscal_position or False
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
            # create the purchase order line
            line_obj.create(cr, uid, {
                'order_id': order.id,
                'name': grid.carrier_id.name,
                'product_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': grid_obj.get_cost(
                    cr, uid, grid.id, order, time.strftime('%Y-%m-%d'),
                    context),
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned': order.date_order,
            })
        return True

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
                                 context=None):
        res = super(purchase_order, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, context=context)
        if order.warehouse_id and not order.dest_address_id:
            res['partner_id'] = order.warehouse_id.partner_id.id,
        return res