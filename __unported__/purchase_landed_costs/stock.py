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
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class stock_move(orm.Model):
    _inherit = "stock.move"

    _columns = {
         'price_unit_net' : fields.float(
            'Purchase Price',
            digits_compute=dp.get_precision('Account'),
            help="This is the net purchase price, without landed cost "
                  "as the price include landed price has been stored in "
                  "price_unit field"),
    }


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"

    def _product_cost_for_average_update(self, cr, uid, move):
        # Be aware of an OpenERP Bug !! If your price_type
        # IS NOT in your comapny currency, AVG price is wrong.
        # Currently, the cost on the product form is supposed to be expressed
        # in the currency of the company owning the product. OpenERP 
        # read the average price from price_get method, which 
        # convert the price to company currency. 
        # So, in case you have:
        #   Rate from CHF to EUR 1.2
        #   Company in CHF
        #   Price type in EUR
        #   Product AVG price = 10.-
        #   Reception new product with cost 15.- (in CHF in price_unit 
        #   of moves)
        #   The price_get will return the current average price in CHF of 12.- 
        #   The price computed will be =(12 * qty + 15 * qty') / (qty + qty')
        #   in CHF. The new cost will be store as is in the procuct 
        #   standard_price instead of converting the result in EUR
        # Reference : https://bugs.launchpad.net/ocb-addons/+bug/1238525
        res = super(stock_partial_picking, self)._product_cost_for_average_update(cr, uid, move)
        _logger.debug('Before res stock_partial_picking `%s`', res)
        # Re-take the cost from the PO line landed_costs field
        if move.purchase_line_id:
            res['cost'] = (move.purchase_line_id.landed_costs /
                           move.purchase_line_id.product_qty)
        _logger.debug('After res stock_partial_picking `%s`', res)
        return res
