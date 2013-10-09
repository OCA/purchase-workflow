# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
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
from osv import osv, fields
import decimal_precision as dp
import logging


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
         'price_unit_net' : fields.float(
            'Purchase Price',
            digits_compute=dp.get_precision('Account'),
            help="This is the net purchase price, without landed cost "
                  "as the price include landed price has been stored in "
                  "price_unit field"),
    }


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _logger = logging.getLogger(__name__)

    def _product_cost_for_average_update(self, cr, uid, move):
        # Be aware of an OpenERP Bug !! If your price_type
        # IS NOT in your comapny currency, AVG price is wrong.
        # Currently, the cost on the product form is supposed to be expressed in the currency
        # of the company owning the product. OpenERP read the average price
        # from price_get method, which convert the price to company currency. 
        # So, in case you have:
        #   Rate from CHF to EUR 1.2
        #   Company in CHF
        #   Price type in EUR
        #   Product AVG price = 10.-
        #   Reception new product with cost 15.- (in CHF in price_unit of moves)
        #   The price_get will return the current average price in CHF of 12.- but the new cost is still
        #   in CHF...
        res = super(stock_partial_picking, self)._product_cost_for_average_update(cr, uid, move)
        self._logger.debug('res stock_partial_picking `%s`', res)
        # Re-take the cost from the PO line landed_costs field
        res['cost'] = move.purchase_line_id.landed_costs / move.purchase_line_id.product_qty
        self._logger.debug('res stock_partial_picking `%s`', res)
        return res
