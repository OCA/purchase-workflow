# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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

from openerp.osv.orm import Model
from openerp import netsvc
from openerp.osv.orm import browse_record, browse_null


class PurchaseOrder(Model):
    _inherit = 'purchase.order'

    def _key_fields_for_grouping(self):
        """Return a list of fields used to identify orders that can be merged.

        Orders that have this fields equal can be merged.

        This function can be extended by other modules to modify the list.
        """
        return ('partner_id', 'location_id', 'pricelist_id')

    def _key_fields_for_grouping_lines(self):
        """Return a list of fields used to identify order lines that can be
        merged.

        Lines that have this fields equal can be merged.

        This function can be extended by other modules to modify the list.
        """
        return ('name', 'date_planned', 'taxes_id', 'price_unit', 'product_id',
                'move_dest_id', 'account_analytic_id')

    def _make_key_for_grouping(self, order, fields):
        """From an order, return a tuple to be used as a key.

        If two orders have the same key, they can be merged.
        """
        key_list = []
        for field in fields:
            field_value = getattr(order, field)

            if isinstance(field_value, browse_record):
                field_value = field_value.id
            elif isinstance(field_value, browse_null):
                field_value = False
            elif isinstance(field_value, list):
                field_value = ((6, 0, tuple([v.id for v in field_value])),)
            key_list.append((field, field_value))
        key_list.sort()
        return tuple(key_list)

    def _can_merge(self, order):
        """Can the order be considered for merging with others?

        This method can be surcharged in other modules.
        """
        return order.state == 'draft'

    def _initial_merged_order_data(self, order):
        """Build the initial values of a merged order."""
        return {
            'origin': order.origin,
            'date_order': order.date_order,
            'partner_id': order.partner_id.id,
            'dest_address_id': order.dest_address_id.id,
            'warehouse_id': order.warehouse_id.id,
            'location_id': order.location_id.id,
            'pricelist_id': order.pricelist_id.id,
            'state': 'draft',
            'order_line': {},
            'notes': '%s' % (order.notes or '',),
            'fiscal_position': (
                order.fiscal_position and order.fiscal_position.id or False
            ),
        }

    def _update_merged_order_data(self, merged_data, order):
        if order.date_order < merged_data['date_order']:
            merged_data['date_order'] = order.date_order
        if order.notes:
            merged_data['notes'] = (
                (merged_data['notes'] or '') + ('\n%s' % (order.notes,))
            )
        if order.origin:
            if (
                order.origin not in merged_data['origin'] and
                merged_data['origin'] not in order.origin
            ):
                merged_data['origin'] = (
                    (merged_data['origin'] or '') + ' ' + order.origin
                )
        return merged_data

    def _group_orders(self, input_orders):
        """Return a dictionary where each element is in the form:

        tuple_key: (dict_of_new_order_data, list_of_old_order_ids)

        """
        key_fields = self._key_fields_for_grouping()
        grouped_orders = {}

        if len(input_orders) < 2:
            return {}

        for input_order in input_orders:
            key = self._make_key_for_grouping(input_order, key_fields)
            if key in grouped_orders:
                grouped_orders[key] = (
                    self._update_merged_order_data(
                        grouped_orders[key][0],
                        input_order
                    ),
                    grouped_orders[key][1] + [input_order.id]
                )
            else:
                grouped_orders[key] = (
                    self._initial_merged_order_data(input_order),
                    [input_order.id]
                )
            grouped_order_data = grouped_orders[key][0]

            for input_line in input_order.order_line:
                line_key = self._make_key_for_grouping(
                    input_line,
                    self._key_fields_for_grouping_lines()
                )
                o_line = grouped_order_data['order_line'].setdefault(
                    line_key, {}
                )
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += (
                        input_line.product_qty *
                        input_line.product_uom.factor /
                        o_line['uom_factor']
                    )
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(input_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = (
                        input_line.product_uom.factor
                        if input_line.product_uom
                        else 1.0)

        return self._cleanup_merged_line_data(grouped_orders)

    def _cleanup_merged_line_data(self, grouped_orders):
        """Remove keys from merged lines, and merges of 1 order."""
        result = {}
        for order_key, (order_data, old_ids) in grouped_orders.iteritems():
            if len(old_ids) > 1:
                for key, value in order_data['order_line'].iteritems():
                    del value['uom_factor']
                    value.update(dict(key))
                order_data['order_line'] = [
                    (0, 0, value)
                    for value in order_data['order_line'].itervalues()
                ]
                result[order_key] = (order_data, old_ids)
        return result

    def _create_new_orders(self, cr, uid, grouped_orders, context=None):
        """Create the new merged orders in the database.

        Return a dictionary that puts the created order ids in relation to the
        original ones, in the form

        new_order_id: [old_order_1_id, old_order_2_id]

        """
        new_old_rel = {}
        for key in grouped_orders:
            new_order_data, old_order_ids = grouped_orders[key]
            new_id = self.create(cr, uid, new_order_data, context=context)
            new_old_rel[new_id] = old_order_ids
        return new_old_rel

    def _fix_workflow(self, cr, uid, new_old_rel):
        """Fix the workflow of the old and new orders.

        Specifically, cancel the old ones and assign workflows to the new ones.

        """
        wf_service = netsvc.LocalService("workflow")
        for new_order_id in new_old_rel:
            old_order_ids = new_old_rel[new_order_id]
            for old_id in old_order_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id,
                                        new_order_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id,
                                        'purchase_cancel', cr)

    def do_merge(self, cr, uid, input_order_ids, context=None):
        """Merge Purchase Orders.

        This method replaces the original one in the purchase module because
        it did not provide any hooks for customization.

        Receive a list of order ids, and return a dictionary where each
        element is in the form:

        new_order_id: [old_order_1_id, old_order_2_id]

        New orders are created, and old orders are deleted.

        """
        input_orders = self.browse(cr, uid, input_order_ids, context=context)
        mergeable_orders = filter(self._can_merge, input_orders)
        grouped_orders = self._group_orders(mergeable_orders)

        new_old_rel = self._create_new_orders(cr, uid, grouped_orders,
                                              context=context)
        self._fix_workflow(cr, uid, new_old_rel)
        return new_old_rel
