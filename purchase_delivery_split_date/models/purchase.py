# -*- coding: utf-8 -*-
# © 2014-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from itertools import groupby
from openerp import models, api

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _get_group_keys(self, order, line, picking_id=False):
        """Define the key that will be used to group. The key should be
        defined as a tuple of dictionaries, with each element containing a
        dictionary element with the field that you want to group by. This
        method is designed for extensibility, so that other modules can add
        additional keys or replace them by others."""
        key = ({'date_planned': line.date_planned},)
        return key

    @api.model
    def _update_picking_from_group_key(self, key, lines):
        """The picking is updated with data from the grouping key.
        This method is designed for extensibility, so that other modules
        can store more data based on new keys."""
        for key_element in key:
            if 'date_planned' in key_element.keys():
                self.date_planned = key_element['date_planned']
        return False

    @api.model
    def _first_picking_copy_vals(self, key, lines):
        """The data to be copied to new pickings is updated with data from the
        grouping key.  This method is designed for extensibility, so that
        other modules can store more data based on new keys."""
        vals = {'move_lines': []}
        for key_element in key:
            if 'date_planned' in key_element.keys():
                vals['date'] = key_element['date_planned']
        return vals

    @api.model
    def _create_stock_moves(self, order, order_lines, picking_id=False):
        """Group the receptions in one picking per group key"""

        # Group the order lines by group key
        order_lines = sorted(order_lines,
                             key=lambda l: self._get_group_keys(
                                 order, l, picking_id=picking_id))
        date_groups = groupby(order_lines, lambda l: self._get_group_keys(
            order, l, picking_id=picking_id))

        # If a picking is provided, use it for the first group only
        if picking_id:
            key, lines = date_groups.next()
            first_picking = self.env['stock.picking'].browse(picking_id)
            self._update_picking_from_group_key(key, lines)
            super(PurchaseOrder, self)._create_stock_moves(
                order, list(lines), picking_id=picking_id)
        else:
            first_picking = False

        for key, lines in date_groups:
            # If a picking is provided, clone it for each key for modularity
            if picking_id:
                copy_vals = self._first_picking_copy_vals(key, lines)
                picking_id = first_picking.copy(copy_vals).id

            super(PurchaseOrder, self)._create_stock_moves(
                order, list(lines), picking_id=picking_id)
