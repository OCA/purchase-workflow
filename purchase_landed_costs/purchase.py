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
from tools.translate import _
        

class landed_cost_position(osv.osv):
    _name = "landed.cost.position"

    _columns = \
      { 'product_id' : fields.many2one('product.product','Landed Cost Name', required=True, domain=[('landed_cost_type','!=', False)]),
        'amount'      : fields.float
            ( 'Amount'
            , required=True
            , digits_compute=dp.get_precision('Purchase Price')
            , help="""Landed cost for stock valuation. It will be added to the price of the supplier price."""),
        'amount_currency': fields.float('Amount Currency', help="The amount expressed in an optional other currency."),
        'currency_id': fields.many2one('res.currency', 'Secondary Currency', help="Optional other currency."),
        'partner_id': fields.many2one('res.partner', 'Partner', help="The supplier of this cost component ."),
        'price_type': fields.selection( [('per_unit','Per Unit'), ('value','Absolute Value')], 'Amount Type', required=True,  \
                  help="Defines if the amount is to be calculated for each quantity or an absolute value"),
        'purchase_order_line_id': fields.many2one('purchase.order.line', 'Purchase Order Line'),
        'purchase_order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'move_line_id': fields.many2one('stock.move', 'Picking Line'),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
      }

landed_cost_position()

#----------------------------------------------------------
# Purchase Line INHERIT
#----------------------------------------------------------
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

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
            if line.order_id.landed_cost_line_ids:
               landed_costs += line.order_id.landed_cost_base_value / line.order_id.amount_total * line.price_subtotal + \
                        line.order_id.landed_cost_base_quantity / line.order_id.quantity_total * line.product_qty
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
        
    _columns = \
       {
         'landed_cost_line_ids': fields.one2many('landed.cost.position', 'purchase_order_line_id', 'Landed Costs Positions'),
         'landing_costs' : fields.function(_landing_cost, digits_compute=dp.get_precision('Account'), string='Landing Costs'),
         'landing_costs_order' : fields.function(_landing_cost_order, digits_compute=dp.get_precision('Account'), string='Landing Costs from Order'),
         'landed_costs' : fields.function(_landed_cost, digits_compute=dp.get_precision('Account'), string='Landed Costs'),
    }

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

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

    def _quantity_total(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        quantity_total = 0.0
        for line in self.browse(cr, uid, ids):
            if line.order_line:
                for pol in line.order_line:
                    if pol.product_qty > 0.0:
                         quantity_total += pol.product_qty
            result[line.id] = quantity_total
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs = 0.0
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs += line.landing_cost_lines + line.amount_untaxed
            result[line.id] = landed_costs

        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_cost_lines = 0.0
        for line in self.browse(cr, uid, ids):
            if line.order_line:
                for pol in line.order_line:
                    if pol.product_qty > 0.0:
                         landed_cost_lines += pol.landing_costs
            result[line.id] = landed_cost_lines
        return result


    _columns = \
        {
         'landed_cost_line_ids': fields.one2many('landed.cost.position', 'purchase_order_id', 'Landed Costs'),
         'landed_cost_base_value' : fields.function(_landed_cost_base_value, digits_compute=dp.get_precision('Account'), string='Landed Costs Base Value'),
         'landed_cost_base_quantity' : fields.function(_landed_cost_base_quantity, digits_compute=dp.get_precision('Account'), string='Landed Costs Base Quantity'),
         'landing_cost_lines' : fields.function(_landing_cost_lines, digits_compute=dp.get_precision('Account'), string='Landing Cost Lines'),
         'landed_cost' : fields.function(_landed_cost, digits_compute=dp.get_precision('Account'), string='Landed Costs Total Untaxed'),
         'quantity_total' : fields.function(_quantity_total, digits_compute=dp.get_precision('Product UoM'), string='Total Quantity'),
    }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order,self)._prepare_order_line_move( cr, uid, order, order_line, picking_id, context)
        
        # FIXME - must create duplicates
        landed_cost_line_ids_dup = order_line.landed_cost_line_ids
        
        res.update({'landed_cost_line_ids' : landed_cost_line_ids_dup})
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(purchase_order,self)._prepare_order_picking( cr, uid, order, context)
        # FIXME - must create duplicates
        landed_cost_line_ids_dup = order_line.landed_cost_line_ids
        res.update({'landed_cost_line_ids' : landed_cost_line_ids_dup})
        return res


purchase_order()
