# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
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
    
    def _landing_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costs for the line
        for line in self.browse(cr, uid, ids):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.price_type == 'value':
                        landed_costs += costs.amount
                    else:
                        landed_costs += costs.amount * line.product_qty
            result[line.id] = landed_costs
        return result

    def _landing_cost_order(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            picking = line.picking_id
            # distrubution of landed costs of PO
            if picking.landed_cost_line_ids:
               if picking.total_amount and picking.total_amount > 0.0:
                   landed_costs += (picking.landed_cost_base_value / picking.total_amount * 
                                    line.price_unit * line.product_qty)
               if picking.quantity_total and picking.quantity_total >0.0:
                   landed_costs +=  (picking.landed_cost_base_quantity / picking.quantity_total * 
                                    line.product_qty)
            result[line.id] = landed_costs
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs +=  line.product_qty * line.price_unit
            result[line.id] = landed_costs
        return result

    def _sub_total(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        sub_total = 0.0
        for line in self.browse(cr, uid, ids):
            sub_total += line.product_qty * line.price_unit_net or 0.0
            result[line.id] = sub_total
        return result

    _columns = { 
         'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'move_line_id',
            'Landed Costs Positions'),
         'landing_costs' : fields.function(
            _landing_cost,
            digits_compute=dp.get_precision('Account'),
            string='Line Landing Costs'),
         'landing_costs_picking' : fields.function(
            _landing_cost_order,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs from Picking'),
         'landed_cost' : fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs'),
         'sub_total' : fields.function(
            _sub_total,
            digits_compute=dp.get_precision('Account'),
            string='Line Sub Total'),
         'price_unit_net' : fields.float(
            'Purchase Price',
            digits_compute=dp.get_precision('Account'),
            help="This is the net purchase price, without landed cost "
                  "as the price include landed price has been stored in"),
    }


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs_base_value = 0.0
        for line in self.browse(cr, uid, ids):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.product_id.landed_cost_type == 'value':
                        landed_costs_base_value += costs.amount
            result[line.id] = landed_costs_base_value
        return result

    def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs_base_quantity = 0.0
        for line in self.browse(cr, uid, ids):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.product_id.landed_cost_type == 'quantity':
                         landed_costs_base_quantity += costs.amount
            result[line.id] = landed_costs_base_quantity
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costs for the line
        for line in self.browse(cr, uid, ids):
            if line.move_lines:
                for ml in line.move_lines:
                    landed_costs += ml.landed_cost 
            result[line.id] = landed_costs
        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_cost_lines = 0.0
        for line in self.browse(cr, uid, ids):
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0:
                         landed_cost_lines += ml.landing_costs + ml.landing_costs_picking
            result[line.id] = landed_cost_lines
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        quantity_total = 0.0
        for line in self.browse(cr, uid, ids):
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0:
                         quantity_total += ml.product_qty
            result[line.id] = quantity_total
        return result

    def _amount_total(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        amount_total = 0.0
        for line in self.browse(cr, uid, ids):
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0 and ml.price_unit:
                         amount_total += ml.sub_total
            result[line.id] = amount_total
        return result

    _columns = { 
         'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'picking_id',
            'Landed Costs Positions'),
         'landed_cost_base_value' : fields.function(
            _landed_cost_base_value,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Value'),
         'landed_cost_base_quantity' : fields.function(
            _landed_cost_base_quantity,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Quantity'),
         'landing_cost_lines' : fields.function(
            _landing_cost_lines,
            digits_compute=dp.get_precision('Account'),
            string='Landing Cost Lines'),
         'landed_cost' : fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total Untaxed'),
         'total_amount' : fields.function(
            _amount_total,
            digits_compute=dp.get_precision('Account'),
            string='Total Product Price'),
         'quantity_total' : fields.function(
            _quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity'),
    }


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _logger = logging.getLogger(__name__)

    def _product_cost_for_average_update(self, cr, uid, move):
       res = super(stock_partial_picking, self)._product_cost_for_average_update(cr, uid, move)
       self._logger.debug('res stock_partial_picking `%s`', res)
       # Re-take the cost from the PO line landed_costs field
       res['cost'] = move.purchase_line_id.landed_costs / move.purchase_line_id.product_qty
       self._logger.debug('res stock_partial_picking `%s`', res)
       return res
