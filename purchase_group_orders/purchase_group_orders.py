# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
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
from openerp.osv.orm import Model, browse_record, browse_null
from openerp.osv import fields
from openerp import netsvc


class procurement_order(Model):
    _inherit = 'procurement.order'

    _columns = {
        'sale_id': fields.many2one(
            'sale.order', 'Sale Order',
            help='the sale order which generated the procurement'),
        'origin': fields.char(
            'Source Document', size=512,
            help="Reference of the document that created this Procurement.\n"
            "This is automatically completed by OpenERP."),
    }

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        """
        Create the purchase order from the procurement, using
        the provided field values, after adding the given purchase
        order line in the purchase order.

           :params procurement: the procurement object generating the purchase
           order

           :params dict po_vals: field values for the new purchase order (the
           ``order_line`` field will be overwritten with one single line, as
           passed in ``line_vals``).

           :params dict line_vals: field values of the single purchase order
           line that the purchase order will contain.

           :return: id of the newly created purchase order

           :rtype: int
        """
        po_vals.update({'order_line': [(0, 0, line_vals)]})
        if procurement.sale_id:
            sale = procurement.sale_id
            update = {'shop_id': sale.shop_id.id,
                      'carrier_id': sale.carrier_id.id}
            po_vals.update(update)
        return self.pool.get('purchase.order').create(cr, uid, po_vals,
                                                      context=context)


class sale_order(Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id,
                                        date_planned, context=None):
        proc_data = super(sale_order, self)._prepare_order_line_procurement(
            cr, uid, order, line,
            move_id, date_planned,
            context)
        proc_data['sale_id'] = order.id
        return proc_data


class purchase_order(Model):
    _inherit = 'purchase.order'

    _columns = {
        'shop_id': fields.many2one(
            'sale.shop', 'Shop',
            help='the shop which generated the sale which triggered the PO'),
        'carrier_id': fields.many2one(
            'delivery.carrier', 'Carrier',
            help='the carrier in charge for delivering the related sale order'
        ),
        'carrier_partner_id': fields.related(
            'carrier_id', 'partner_id',
            type='many2one',
            relation='res.partner',
            string='Carrier Name',
            readonly=True,
            help="Name of the carrier partner in charge of delivering the "
            "related sale order"),
        'origin': fields.char(
            'Source Document', size=512,
            help="Reference of the document that generated this purchase "
            "order request."),
    }

    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders have same stock location, same pricelist
        * Purchase Orders have the same shop and the same carrier
          (NEW in this module)

        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit
        """
        # TOFIX: merged order line should be unlink
        wf_service = netsvc.LocalService("workflow")

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'move_dest_id',
                             'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # compute what the new orders should contain
        new_orders = {}
        for porder in [
            order for order in self.browse(cr, uid, ids, context=context)
            if order.state == 'draft'
        ]:
            order_key = make_key(
                porder, ('partner_id', 'location_id', 'pricelist_id',
                         'shop_id', 'carrier_id'))  # added line
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'partner_address_id': porder.partner_address_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id': porder.warehouse_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and
                    porder.fiscal_position.id or False,
                    # added line
                    'shop_id': porder.shop_id and
                    porder.shop_id.id,
                    # added line
                    'carrier_id': porder.carrier_id and porder.carrier_id.id,
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (
                        order_infos['notes'] or ''
                    ) + ('\n%s' % (porder.notes,))
                if porder.origin:
                    order_infos['origin'] = (
                        order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                line_key = make_key(
                    order_line,
                    ('name', 'date_planned', 'taxes_id', 'price_unit', 'notes',
                     'product_id', 'move_dest_id', 'account_analytic_id'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += (
                        order_line.product_qty *
                        order_line.product_uom.factor /
                        o_line['uom_factor']
                    )
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = (
                        order_line.product_uom and
                        order_line.product_uom.factor or 1.0
                    )

        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [
                (0, 0, value)
                for value in order_data['order_line'].itervalues()
            ]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(
                    uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(
                    uid, 'purchase.order', old_id, 'purchase_cancel', cr)
        return orders_info
