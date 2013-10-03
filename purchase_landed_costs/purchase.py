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
from tools.translate import _
import logging


class landed_cost_position(osv.osv):
    """The landed cost position represent a direct cost for the delivery 
    of the goods puchased. It can be from a different partner than the 
    original supplier, like transport. Cost will be re-affected to each PO line
    in respect of the distribution method selected. The average price 
    computation for the product will take those direct costs into account."""

    _name = "landed.cost.position"

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Landed Cost Name',
            required=True,
            domain=[('landed_cost_type','!=', False)]),
        'account_id': fields.many2one(
            'account.account',
            'Fiscal Account',
            required=True,),
        'amount': fields.float
            ('Amount',
            required=True,
            digits_compute=dp.get_precision('Purchase Price'),
            help="Landed cost for stock valuation. It will be added to the price "
                 "of the supplier price."),
        'amount_currency': fields.float(
            'Amount Currency',
            help="The amount expressed in an optional other currency."),
        'currency_id': fields.many2one(
            'res.currency',
            'Secondary Currency',
            help="Optional other currency."),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            help="The supplier of this cost component.",
            required=True),
        'price_type': fields.selection(
            [('per_unit','Per Quantity'),
             ('value','Absolute Value')],
            'Amount Type',
            required=True,
            help="Defines if the amount is to be calculated for each quantity "
                 "or an absolute value"),
        'purchase_order_line_id': fields.many2one(
            'purchase.order.line',
            'Purchase Order Line'),
        'purchase_order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'move_line_id': fields.many2one('stock.move', 'Picking Line'),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'generate_invoice': fields.boolean(
            'Generate Invoice',
            help="If ticked, this will generate a draft invoice at the picking creation "
                 "for this landed cost position from the related partner. If not, no "
                 "invoice will be generated, but the cost will be included for the average "
                 "price computation."),
      }

    _default = {
        'generate_invoice': False,
    }

    def onchange_product_id(self, cr, uid, ids, product_id, 
            purchase_order_id=False, context=None):
        res = {}
        fiscal_position = False
        if product_id:
            prod_obj = self.pool.get('product.product')
            prod = prod_obj.browse(cr, uid, [product_id], context=context)[0]
            if purchase_order_id:
                po_obj = self.pool.get('purchase.order')
                po = po_obj.browse(cr, uid, [purchase_order_id], context=context)[0]
                fiscal_position = po.fiscal_position or False
            account_id = prod_obj._choose_exp_account_from(cr, uid, prod, 
                fiscal_position=fiscal_position, context=context)
            value = {
                'price_type': prod.landed_cost_type,
                'account_id': account_id}
            res = {'value': value}
        return res


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def _landing_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        # landed costss for the line
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

    def _landing_cost_order(self, cr, uid, ids, name, args, context):
        if not ids:
            return {}
        result = {}
        lines = self.browse(cr, uid, ids)
        # Landed costs line by line
        for line in lines:
            landed_costs = 0.0
            order = line.order_id
            # distribution of landed costs of PO
            if order.landed_cost_line_ids:
                # Base value (Absolute Value)
                if order.landed_cost_base_value:
                    landed_costs += (order.landed_cost_base_value / 
                                 order.amount_total * line.price_subtotal)
                # Base quantity (Per Quantity)
                if order.landed_cost_base_quantity:
                    landed_costs += (order.landed_cost_base_quantity / 
                                 order.quantity_total * line.product_qty)
            result[line.id] = landed_costs
        return result

    def _landing_cost_factor(self, cr, uid, ids, name, args, context):
        """
        Calculates the percentage of landing costs that should be put on 
        this order line
        """
        for line in self.browse(cr, uid, ids):
            if line.landed_cost_line_ids:
                pass

    def _landed_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            landed_costs = 0.0
            landed_costs += (line.price_subtotal + 
                             line.landing_costs +  line.landing_costs_order)
            result[line.id] = landed_costs
        return result
        
    _columns = {
         'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'purchase_order_line_id',
            'Landed Costs Positions'),
         'landing_costs': fields.function(
            _landing_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs'),
         'landing_costs_order': fields.function(
            _landing_cost_order,
            digits_compute=dp.get_precision('Account'),
            string='Landing Costs from Order'),
         'landed_costs': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs'),
    }


class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _logger = logging.getLogger(__name__)

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        result = {}
        landed_costs_base_value = 0.0
        for line in self.browse(cr, uid, ids):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if costs.price_type == 'value':
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
                    if costs.price_type == 'per_unit':
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
            landed_costs += (line.landing_cost_lines + line.landed_cost_base_value + 
                             line.landed_cost_base_quantity + line.amount_untaxed)
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

    _columns = {
         'landed_cost_line_ids': fields.one2many(
            'landed.cost.position',
            'purchase_order_id',
            'Landed Costs'),
         'landed_cost_base_value': fields.function(
            _landed_cost_base_value,
            digits_compute=dp.get_precision('Account'), 
            string='Landed Costs Base Value'),
         'landed_cost_base_quantity': fields.function(
            _landed_cost_base_quantity,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Base Quantity'),
         'landing_cost_lines': fields.function(
            _landing_cost_lines,
            digits_compute=dp.get_precision('Account'),
            string='Landing Cost Lines'),
         'landed_cost': fields.function(
            _landed_cost,
            digits_compute=dp.get_precision('Account'),
            string='Landed Costs Total Untaxed'),
         'quantity_total': fields.function(
            _quantity_total,
            digits_compute=dp.get_precision('Product UoM'),
            string='Total Quantity'),
    }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
            context=None):
        res = super(purchase_order,self)._prepare_order_line_move(cr, uid, order, 
            order_line, picking_id, context=context)
        res['price_unit_net'] =  res['price_unit']
        res['price_unit'] = order_line.landed_costs / order_line.product_qty        
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(purchase_order,self)._prepare_order_picking( cr, uid,
            order, context)
        return res

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id, 
            landed_cost, context=None):
        """Collects require data from landed cost position that is used to 
        create invoice line for that particular position
        :param account_id: Expense account.
        :param inv_id: Related invoice.
        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        return {
            'name': landed_cost.product_id.name,
            'account_id': account_id,
            'invoice_id' : inv_id,
            'price_unit': landed_cost.amount or 0.0,
            'quantity': 1.0,
            'product_id': landed_cost.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in 
                landed_cost.product_id.supplier_taxes_id])],
        }

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        """Collects require data from landed cost position that is used to
        create invoice for that particular position
        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice.
        :rtype: dict
        """
        currency_id = (landed_cost.currency_id.id or 
                landed_cost.purchase_order_id.company_id.currency_id.id)
        fiscal_position = landed_cost.purchase_order_id.fiscal_position or False
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),
            ('company_id', '=', order.company_id.id)], limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') 
                    % (order.company_id.name, order.company_id.id))
        return {
            'partner_id' : landed_cost.partner_id.id,
            'currency_id': currency_id,
            'account_id': landed_cost.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'origin': landed_cost.purchase_order_id.name,
            'fiscal_position':  fiscal_position,
            'company_id': landed_cost.purchase_order_id.company_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
        }

    def action_invoice_create(self, cr, uid, ids, context=None):
        """On invoices creation of the PO, generate as well all invoices
        for all landed cost position. Remember that only landed cost position with
        the checkbox generate_invoice ticked are generated."""
        res =  super(purchase_order,self).action_invoice_create(cr, uid, ids,
            context=context)
        invoice_obj = self.pool.get('account.invoice')
        prod_obj = self.pool.get('product.product')
        invoice_line_obj = self.pool.get('account.invoice.line')
        for order in self.browse(cr, uid, ids, context=context):
            invoice_ids = []
            for order_cost in order.landed_cost_line_ids:
                if order_cost.generate_invoice:
                    vals_inv = self._prepare_landed_cost_inv(cr, uid, 
                        order_cost, context=context)
                    self._logger.debug('vals inv`%s`', vals_inv)
                    inv_id = invoice_obj.create(cr, uid, vals_inv, context=context)
                    fiscal_position = (order_cost.purchase_order_id.fiscal_position 
                        or False)
                    exp_account_id = self._choose_exp_account_from(cr, uid,
                            order_cost.product_id,
                            fiscal_position=fiscal_position,
                            context=context)
                    vals_line = self._prepare_landed_cost_inv_line(cr, uid,
                        exp_account_id, inv_id, order_cost, context=context)
                    self._logger.debug('vals line `%s`', vals_line)
                    inv_line_id = invoice_line_obj.create(cr, uid, vals_line,
                        context=context)
                    invoice_ids.append(inv_id)
            # Link this new invoice to related purchase order
            # 4 in that list is "Add" mode in a many2many used here because
            # the call to super() already add the main invoice
            if invoice_ids:
                commands = [(4, invoice_id) for invoice_id in invoice_ids]
                order.write({'invoice_ids': commands}, context=context)
        return res
