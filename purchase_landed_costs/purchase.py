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
from tools.translate import _
import logging


class landed_cost_position(osv.osv):
    """The landed cost position represent a direct cost for the delivery 
    of the goods puchased. It can be from a different partner than the 
    original supplier, like transport. Cost will be re-affected to each PO line
    in respect of the distribution method selected. The average price 
    computation for the product will take those direct costs into account."""

    _name = "landed.cost.position"

    def _amount_total(self, cr, uid, ids, name, args, context):
    # TODO: We should have a field that is the computed value
    # e.g. if it's related to a line and per_unit => I want for the reporting
    # the total line landed cost. Name the field amount_total and show this 
    # one in analysis view. This field is computed with:
    # if purchase_order_line_id and per_unit = amount * purchase_order_line_id.product_qty
    # else = amount
        if not ids : return {}
        result = {}
        # landed costss for the line
        for line in self.browse(cr, uid, ids):
            if line.purchase_order_line_id and line.price_type == 'per_unit':
                result[line.id] = (line.amount * 
                    line.purchase_order_line_id.product_qty)
            else:
                result[line.id] = line.amount
        return result

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
            help="Landed cost for stock valuation (expressed in company default currency). "
                 "It will be added to the price of the supplier price."),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            help="The supplier of this cost component.",
            required=True),
        'price_type': fields.selection(
            [('per_unit','Per Quantity'),
             ('value','Absolute Value')],
            'Distribution Type',
            required=True,
            help="Defines if the amount is to be calculated for each quantity "
                 "or an absolute value"),
        'purchase_order_line_id': fields.many2one(
            'purchase.order.line',
            'Purchase Order Line'),
        'purchase_order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'generate_invoice': fields.boolean(
            'Generate Invoice',
            help="If ticked, this will generate a draft invoice at the PO confirmation "
                 "for this landed cost position from the related partner. If not, no "
                 "invoice will be generated, but the cost will be included for the average "
                 "price computation."),
        'amount_total': fields.function(
            _amount_total,
            digits_compute=dp.get_precision('Account'),
            string='Amount Total',
            help="This field represent the total amount of this position "
                 "regarding a whole order. By summing it, you'll have the total "
                 "landed cost for the order",
            store=True),
        'date_po': fields.related('purchase_order_id', 'date_order', type='date',
            string='Date',
            store=True,
            readonly=True,
            help="Date of the related PO"),
        'company_id': fields.many2one('res.company','Company',
            required=True,
            select=1,),
      }

    _default = {
        'generate_invoice': False,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(
            cr, uid, 'purchase.order', context=c),
    }

    def write(self, cr, uid, ids, vals, context=None):
        """Add the purchase_order_id if only linked to a line"""
        if vals.get('purchase_order_line_id'):
            po = self.pool.get('purchase.order.line').browse(cr, uid, 
                vals['purchase_order_line_id'], context=context).order_id
            vals['purchase_order_id'] = po.id
        return super(landed_cost_position, self).write(cr, uid, ids, 
            vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """Add the purchase_order_id if only linked to a line"""
        if vals.get('purchase_order_line_id'):
            po = self.pool.get('purchase.order.line').browse(cr, uid, 
                vals['purchase_order_line_id'], context=context).order_id
            vals['purchase_order_id'] = po.id
        return super(landed_cost_position, self).create(cr, uid, vals, 
            context=context)

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
                                 order.amount_untaxed * line.price_subtotal)
                # Base quantity (Per Quantity)
                if order.landed_cost_base_quantity:
                    landed_costs += (order.landed_cost_base_quantity / 
                                 order.quantity_total * line.product_qty)
            result[line.id] = landed_costs
        return result

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
            'Landed Costs',
            domain=[('purchase_order_line_id','=',False)]),
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
        """Here, the technical price_unit field will store the purchase price + 
        landed cost. The original purchase price is stored in price_unit_net new
        field to keep record of it."""
        res = super(purchase_order,self)._prepare_order_line_move(cr, uid, order, 
            order_line, picking_id, context=context)
        res['price_unit_net'] =  res['price_unit']
        res['price_unit'] = order_line.landed_costs / order_line.product_qty        
        return res

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id, 
            landed_cost, context=None):
        """Collects require data from landed cost position that is used to 
        create invoice line for that particular position.
        If it comes from a PO line and Distribution type is per unit
        the quantity of the invoice is the PO line quantity
        :param account_id: Expense account.
        :param inv_id: Related invoice.
        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        qty = 1.0
        if (landed_cost.purchase_order_line_id and 
            landed_cost.price_type == 'per_unit'):
            qty = landed_cost.purchase_order_line_id.product_qty
        return {
            'name': landed_cost.product_id.name,
            'account_id': account_id,
            'invoice_id' : inv_id,
            'price_unit': landed_cost.amount or 0.0,
            'quantity': qty,
            'product_id': landed_cost.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in 
                landed_cost.product_id.supplier_taxes_id])],
        }

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        """Collects require data from landed cost position that is used to
        create invoice for that particular position. Note that _landed
        can come from a line or at whole PO level.
        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice.
        :rtype: dict
        """
        po = (landed_cost.purchase_order_id or
            landed_cost.purchase_order_line_id.order_id)
        currency_id = (landed_cost.currency_id.id or 
                po.company_id.currency_id.id)
        fiscal_position = po.fiscal_position or False
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),
            ('company_id', '=', po.company_id.id)], limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') 
                    % (po.company_id.name, 
                        po.company_id.id))
        return {
            'partner_id' : landed_cost.partner_id.id,
            'currency_id': currency_id,
            'account_id': landed_cost.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'origin': po.name,
            'fiscal_position':  fiscal_position,
            'company_id': po.company_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
        }

    def _generate_invoice_from_landed_cost(self, cr, uid, landed_cost, 
            context=None):
        """Generate an invoice from order landed costs (means generic 
            costs to a whole PO) or from a line landed costs."""
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        prod_obj = self.pool.get('product.product')
        po = (landed_cost.purchase_order_id or
            landed_cost.purchase_order_line_id.order_id)
        vals_inv = self._prepare_landed_cost_inv(cr, uid, 
            landed_cost, context=context)
        self._logger.debug('vals inv`%s`', vals_inv)
        inv_id = invoice_obj.create(cr, uid, vals_inv, context=context)
        fiscal_position = (po.fiscal_position or False)
        exp_account_id = prod_obj._choose_exp_account_from(cr, uid,
                landed_cost.product_id,
                fiscal_position=fiscal_position,
                context=context)
        vals_line = self._prepare_landed_cost_inv_line(cr, uid,
            exp_account_id, inv_id, landed_cost, context=context)
        self._logger.debug('vals line `%s`', vals_line)
        inv_line_id = invoice_line_obj.create(cr, uid, vals_line,
            context=context)
        return inv_id

    def wkf_approve_order(self, cr, uid, ids, context=None):
        """On PO approval, generate all invoices
        for all landed cost position. Remember that only landed cost position with
        the checkbox generate_invoice ticked are generated."""
        res = super(purchase_order,self).wkf_approve_order(cr, uid, ids,
            context=context)
        for order in self.browse(cr, uid, ids, context=context):
            invoice_ids = []
            for order_cost in order.landed_cost_line_ids:
                if order_cost.generate_invoice:
                    inv_id = self._generate_invoice_from_landed_cost(cr, uid, 
                        order_cost, context=context)
                    invoice_ids.append(inv_id)
            for po_line in order.order_line:
                for line_cost in po_line.landed_cost_line_ids:
                    inv_id = self._generate_invoice_from_landed_cost(cr, uid, 
                        line_cost, context=context)
                    invoice_ids.append(inv_id)
            # Link this new invoice to related purchase order
            # 4 in that list is "Add" mode in a many2many used here because
            # the call to super() already add the main invoice
            if invoice_ids:
                commands = [(4, invoice_id) for invoice_id in invoice_ids]
                order.write({'invoice_ids': commands}, context=context)
        return res

