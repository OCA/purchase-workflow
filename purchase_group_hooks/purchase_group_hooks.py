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


class PurchaseOrder(Model):
    _inherit = 'purchase.order'

    @staticmethod
    def _key_fields_for_grouping():
        """Return a list of fields used to identify orders that can be merged.

        Orders that have this fields equal can be merged.

        This function can be extended by other modules to modify the list.
        """
        return ['partner_id', 'location_id', 'pricelist_id']

    @staticmethod
    def _make_key_for_grouping(order, fields):
        """From an order, return a tuple to be used as a key.

        If two orders have the same key, they can be merged.
        """
        key_list = [getattr(order, field) for field in fields]
        return key_list

    @staticmethod
    def _group_orders(input_orders):
        """Return a dictionary where each element is in the form:

        key_tuple: (new_order_data_dictionary, list_of_old_order_ids)

        """
        return {}

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

    @staticmethod
    def _fix_workflow(new_old_rel):
        """Fix the workflow of the old and new orders.

        Specifically, cancel the old ones and assign workflows to the new ones.

        """
        wf_service = netsvc.LocalService("workflow")
        for new_order_id in new_old_rel:
            old_order_ids = new_old_rel[new_order_id]
            for old_id in old_order_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)

    def do_merge(self, cr, uid, input_order_ids, context=None):
        """Merge Purchase Orders.

        This method replace the original one in the purchase module because
        it did not provide any hooks for customization.

        Receive a list of order ids, and return a dictionary where each
        element is in the form:

        new_order_id: [old_order_1_id, old_order_2_id]

        New orders are created, and old orders are deleted.

        """
        input_orders = self.browse(cr, uid, input_order_ids, context=context)

        grouped_orders = self._group_orders(input_orders)

        new_old_rel = self._create_new_orders(cr, uid, grouped_orders, context=context)
        self._fix_workflow(new_old_rel)
        return new_old_rel
