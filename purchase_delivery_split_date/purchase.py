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
    def _create_stock_moves(self, order, order_lines, picking_id=False):
        """Group the receptions in one picking per expected date"""

        # Group the order lines by delivery date
        order_lines = sorted(order_lines, key=lambda l: l.date_planned)
        date_groups = groupby(order_lines, lambda l: l.date_planned)

        # If a picking is provided, use it for the first group only
        if picking_id:
            delivery_date, lines = date_groups.next()
            first_picking = self.env['stock.picking'].browse(picking_id)
            first_picking.date = delivery_date
            super(PurchaseOrder, self)._create_stock_moves(
                order, list(lines), picking_id=picking_id)

        for delivery_date, lines in date_groups:
            # If a picking is provided, clone it for each date for modularity
            if picking_id:
                picking_id = first_picking.copy({'move_lines': [],
                                                 'date': delivery_date}).id

            super(PurchaseOrder, self)._create_stock_moves(
                order, list(lines), picking_id=picking_id)
