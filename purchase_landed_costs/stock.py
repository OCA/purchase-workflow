# -*- coding: utf-8 -*-
from osv import orm, fields
import decimal_precision as dp
import logging
#----------------------------------------------------------
#  Stock Move
#----------------------------------------------------------


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _landing_cost(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids):
            landed_costs = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.price_type == 'value':
                        landed_costs += costs.amount
                    else:
                        landed_costs += costs.amount * line.product_qty
            result[line.id] = landed_costs
        return result

    def _landing_cost_order(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids):
            landed_costs = 0.0
            # distrubution of landed costs of PO
            if line.picking_id.landed_cost_line_ids:
                if line.picking_id.total_amount \
                        and line.picking_id.total_amount > 0.0:
                    landed_costs += line.picking_id.landed_cost_base_value \
                            / line.picking_id.total_amount \
                            * line.price_unit * line.product_qty
                if line.picking_id.quantity_total  \
                        and line.picking_id.quantity_total > 0.0:
                    landed_costs += line.picking_id.landed_cost_base_quantity \
                            / line.picking_id.quantity_total * line.product_qty
            result[line.id] = landed_costs

        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.product_qty * line.price_unit

        return result

    def _sub_total(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.product_qty * line.price_unit_net or 0.0

        return result

    _columns = {
         'landed_cost_line_ids': fields.one2many('landed.cost.position',
                 'move_line_id', 'Landed Costs Positions'),
         'landing_costs': fields.function(_landing_cost,
                 digits_compute=dp.get_precision('Account'),
                 string='Line Landing Costs'),
         'landing_costs_picking': fields.function(_landing_cost_order,
                 digits_compute=dp.get_precision('Account'),
                 string='Landing Costs from Picking'),
         'landed_cost': fields.function(_landed_cost,
                 digits_compute=dp.get_precision('Account'),
                 string='Landed Costs'),
         'sub_total': fields.function(_sub_total,
                 digits_compute=dp.get_precision('Account'),
                 string='Line Sub Total'),
         'price_unit_net': fields.float('Purchase Price',
                 digits_compute=dp.get_precision('Account'))
    }

stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids):
            landed_costs_base_value = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.product_id.landed_cost_type == 'value':
                        landed_costs_base_value += costs.amount
            result[line.id] = landed_costs_base_value
        return result

    def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids):
            landed_costs_base_quantity = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.product_id.landed_cost_type == 'quantity':
                        landed_costs_base_quantity += costs.amount
            result[line.id] = landed_costs_base_quantity
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs = 0.0
            if line.move_lines:
                for ml in line.move_lines:
                    landed_costs += ml.landed_cost
            result[line.id] = landed_costs

        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids):
            landed_cost_lines = 0.0
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0:
                        landed_cost_lines += ml.landing_costs \
                                + ml.landing_costs_picking
            result[line.id] = landed_cost_lines
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context):
        if not ids:
            return {}
        result = {}
        for line in self.browse(cr, uid, ids):
            quantity_total = 0.0
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0:
                        quantity_total += ml.product_qty
            result[line.id] = quantity_total
        return result

    def _amount_total(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = dict()
        if not ids:
            return {}
        result = {}
        stock_picking_lines = self.browse(cr, uid, ids)
        for line in stock_picking_lines:
            amount_total = 0.0
            if line.move_lines:
                for ml in line.move_lines:
                    if ml.product_qty > 0.0 and ml.price_unit:
                        amount_total += ml.sub_total
            result[line.id] = amount_total
        return result

    def _get_price_unit_invoice(self, cursor, user, move_line,
                                type):
        if move_line.purchase_line_id:
            if move_line.purchase_line_id.order_id.invoice_method == 'picking':
                return move_line.price_unit_net
            else:
                return move_line.purchase_line_id.price_unit
        return super(stock_picking, self)._get_price_unit_invoice(cursor,
                                                        user, move_line, type)

    _columns = {
         'landed_cost_line_ids': fields.one2many('landed.cost.position',
                                                 'picking_id',
                                                 'Landed Costs Positions'),
         'landed_cost_base_value': fields.function(_landed_cost_base_value,
             digits_compute=dp.get_precision('Account'),
             string='Landed Costs Base Value'),
         'landed_cost_base_quantity': fields.function(
            _landed_cost_base_quantity,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Quantity'),
         'landing_cost_lines': fields.function(_landing_cost_lines,
            digits_compute=dp.get_precision('Account'),
            string='Landing Cost Lines'),
         'landed_cost': fields.function(_landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total Untaxed'),
         'total_amount': fields.function(_amount_total,
            digits_compute=dp.get_precision('Account'),
            string='Total Product Price'),
         'quantity_total': fields.function(_quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity')
    }

stock_picking()


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"
    _logger = logging.getLogger(__name__)

    def _product_cost_for_average_update(self, cr, uid, move):
        res = super(stock_partial_picking, self).\
            _product_cost_for_average_update(cr, uid, move)
        self._logger.debug('res stock_partial_picking `%s`', res)
        res['cost'] = move.landed_cost / move.product_qty
        self._logger.debug('res stock_partial_picking `%s`', res)
        return res

stock_partial_picking()
