# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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


#----------------------------------------------------------
#  Stock Move
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    def _landing_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costss for the line
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
            # distrubution of landed costs of PO
            if line.picking_id.landed_cost_line_ids:
               landed_costs += line.picking_id.landed_cost_base_value / line.picking_id.total_amount * line.price_unit * line.product_qty + \
                        line.picking_id.landed_cost_base_quantity / line.picking_id.quantity_total * line.product_qty
            result[line.id] = landed_costs

        return result

    def _landed_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs += line.price_subtotal + line.landing_costs +  line.landing_costs_order
            result[line.id] = landed_costs

        return result

    _columns = { 
         'landed_cost_line_ids': fields.one2many('landed.cost.position', 'move_line_id', 'Landed Costs Positions'),
         'landing_costs' : fields.function(_landing_cost, digits_compute=dp.get_precision('Account'), string='Landing Costs'),
         'landing_costs_picking' : fields.function(_landing_cost_order, digits_compute=dp.get_precision('Account'), string='Landing Costs from Picking'),
         'landed_cost' : fields.function(_landed_cost, digits_compute=dp.get_precision('Account'), string='Landed Costs'),
    }

stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
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
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs += line.landing_cost_lines + line.total_amount
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
                         landed_cost_lines += ml.landing_costs
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
                         amount_total += ml.product_qty * ml.price_unit
            result[line.id] = amount_total
        return result


    _columns = { 
         'landed_cost_line_ids': fields.one2many('landed.cost.position', 'picking_id', 'Landed Costs Positions'),
         'landed_cost_base_value' : fields.function(_landed_cost_base_value, digits_compute=dp.get_precision('Account'), string='Landed Costs Base Value'),
         'landed_cost_base_quantity' : fields.function(_landed_cost_base_quantity, digits_compute=dp.get_precision('Account'), string='Landed Costs Base Quantity'),
         'landing_cost_lines' : fields.function(_landing_cost_lines, digits_compute=dp.get_precision('Account'), string='Landing Cost Lines'),
         'landed_cost' : fields.function(_landed_cost, digits_compute=dp.get_precision('Account'), string='Landed Costs Total Untaxed'),
         'total_amount' : fields.function(_amount_total, digits_compute=dp.get_precision('Account'), string='Total Product Price'),
         'quantity_total' : fields.function(_quantity_total, digits_compute=dp.get_precision('Product UoM'), string='Total Quantity'),
    }

stock_picking()


