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
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class landed_cost_distribution_type(orm.Model):
    """ This is a model to give how we should distribute the amount given
    for a landed costs. At the begining we use a selection field, but it
    was impossible to filter it depending on the context (in a line or
    on order). So we replaced it by this object, adding is_* method to
    deal with. Base distribution are defined in YML file.

    """

    _name = "landed.cost.distribution.type"

    _columns = {
        'name': fields.char('Distribution Type', required=True),
        'apply_on': fields.selection(
            [('line', 'Line'),
             ('order', 'Order')],
            'Applied on',
            required=True,
            help="Defines if this distribution type Applied "
                 "on order or line level."),
        'landed_cost_type': fields.selection(
            [('value', 'Value'),
             ('per_unit', 'Quantity')],
            'Product Landed Cost Type',
            help="Refer to the product landed cost type."),
    }


class landed_cost_position(orm.Model):
    """ The landed cost position represent a direct cost for the delivery
    of the goods puchased. It can be from a different partner than the
    original supplier, like transport. Cost will be re-affected to each
    PO line in respect of the distribution method selected. The average
    price computation for the product will take those direct costs into
    account.

    """

    _name = "landed.cost.position"

    def _get_company_currency_from_landed_cost(self, cr, uid, landed_cost,
                                               amount, context=None):
        """ Return the amount in company currency by looking at the po.

        Always return a value, even if company currency = PO one.

        :param browse_record landed_cost: Landed cost position browse record
        :param float value to convert
        :return: Float value amount in company currency converted at po date

        """
        cur_obj = self.pool.get('res.currency')
        result = amount
        # In some cases, po is not set, we must take it back from po_line
        if landed_cost.purchase_order_id:
            po = landed_cost.purchase_order_id
        else:
            po = landed_cost.purchase_order_line_id.order_id
        if po:
            cmp_cur_id = po.company_id.currency_id.id
            po_cur_id = po.pricelist_id.currency_id.id
            if cmp_cur_id != po_cur_id:
                ctx = context.copy()
                ctx['date'] = landed_cost.date_po or False
                result = cur_obj.compute(cr, uid,
                                         po_cur_id,
                                         cmp_cur_id,
                                         amount,
                                         context=ctx)
        return result

    def _get_total_amount(self, cr, uid, landed_cost, context=None):
        """ We should have a field that is the computed value (total
        costs that land) e.g. if it's related to a line and per_unit =>
        I want for the reporting the total line landed cost and multiply
        the quantity by given amount.

        :param browse_record landed_cost: Landed cost position browse record
        :return total value of this landed cost position

        """
        vals_po_currency = 0.0
        if (landed_cost.purchase_order_line_id and
                landed_cost.distribution_type_id.landed_cost_type == 'per_unit'):
            vals_po_currency = (landed_cost.amount *
                                landed_cost.purchase_order_line_id.product_qty)
        else:
            vals_po_currency = landed_cost.amount
        return vals_po_currency

    def _get_amounts(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        result = {}
        for landed_cost in self.browse(cr, uid, ids, context=context):
            val_comp_currency = self._get_company_currency_from_landed_cost(
                cr, uid, landed_cost, landed_cost.amount, context=context)
            val_total = self._get_total_amount(cr, uid, landed_cost,
                                               context=context)
            val_total_comp_currency = self._get_company_currency_from_landed_cost(
                cr, uid, landed_cost, val_total, context=context)
            amounts = {
                'amount_company_currency': val_comp_currency,
                'amount_total': val_total,
                'amount_total_comp_currency': val_total_comp_currency
            }
            result[landed_cost.id] = amounts
        return result

    def _get_po(self, cr, uid, ids, context=None):
        landed_obj = self.pool.get('landed.cost.position')
        return landed_obj.search(cr, uid,
                                 [('purchase_order_id', 'in', ids)],
                                 context=context)

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Landed Cost Name',
            required=True,
            domain=[('landed_cost_type', '!=', False)]),
        'account_id': fields.many2one(
            'account.account',
            'Fiscal Account',
            required=True,),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            help="The supplier of this cost component.",
            required=True),
        'distribution_type_id': fields.many2one(
            'landed.cost.distribution.type',
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
            help="If ticked, this will generate a draft invoice at the "
                 "PO confirmation for this landed cost position from the "
                 "related partner. If not, no invoice will be generated, "
                 "but the cost will be included for the average price "
                 "computation."),
        'amount': fields.float(
            'Amount',
            required=True,
            digits_compute=dp.get_precision('Purchase Price'),
            help="Landed cost expressed in PO currency used "
                 "to fullfil landed cost."),
        'amount_company_currency': fields.function(
            _get_amounts,
            type="float",
            multi='compute_amounts',
            string='Amount Company Currency',
            # Use Account as it's for comparison with financial accounting
            digits_compute=dp.get_precision('Account'),
            store={
                'purchase.order': (_get_po,
                                   ['pricelist_id', 'company_id'], 50),
                'landed.cost.position': (lambda self, cr, uid, ids, c=None: ids,
                                          ['amount', 'purchase_order_id'], 10),
            },
            help="Landed cost for stock valuation (expressed in company currency). "
                 "It will be added to the price of the supplier price."),
        'amount_total': fields.function(
            _get_amounts,
            type="float",
            multi='compute_amounts',
            digits_compute=dp.get_precision('Purchase Price'),
            string='Amount Total',
            help="This field represent the total amount of this position "
                 "regarding a whole order. By summing it, you'll have the total "
                 "landed cost for the order (in his currency)",
            store={
                'purchase.order': (_get_po,
                                   ['pricelist_id', 'company_id'], 50),
                'landed.cost.position': (lambda self, cr, uid, ids, c=None: ids,
                                          ['amount', 'purchase_order_id'], 10)
            }),
        'amount_total_comp_currency': fields.function(
            _get_amounts,
            type="float",
            multi='compute_amounts',
            digits_compute=dp.get_precision('Account'),
            string='Amount Total Company Currency',
            help="This field represent the total amount of this position "
                 "regarding a whole order. By summing it, you'll have the total "
                 "landed cost for the order (in company reference currency).",
            store={
                'purchase.order': (_get_po,
                                   ['pricelist_id', 'company_id'], 50),
                'landed.cost.position': (lambda self, cr, uid, ids, c=None: ids,
                                          ['amount', 'purchase_order_id'], 10)
            }),
        'date_po': fields.related(
            'purchase_order_id', 'date_order',
            type='date',
            string='Date',
            store=True,
            readonly=True,
            help="Date of the related PO"),
        'company_id': fields.related(
            'purchase_order_id', 'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            store=True,
            readonly=True),
      }

    _default = {
        'generate_invoice': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        """ Add the purchase_order_id if only linked to a line """
        if vals.get('purchase_order_line_id'):
            po_line_obj = self.pool.get('purchase.order.line')
            line_id = vals['purchase_order_line_id']
            po = po_line_obj.browse(cr, uid, line_id, context=context).order_id
            vals['purchase_order_id'] = po.id
        return super(landed_cost_position, self).write(
            cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """ Add the purchase_order_id if only linked to a line """
        if vals.get('purchase_order_line_id'):
            po_line_obj = self.pool.get('purchase.order.line')
            line_id = vals['purchase_order_line_id']
            po = po_line_obj.browse(cr, uid, line_id, context=context).order_id
            vals['purchase_order_id'] = po.id
        return super(landed_cost_position, self).create(
            cr, uid, vals, context=context)

    def onchange_product_id(self, cr, uid, ids, product_id,
                            purchase_order_id=False, context=None):
        """ Give the default value for the distribution type depending
        on the setting of the product and the use case: line or order
        position.

         """
        res = {}
        fiscal_position = False
        landed_cost_type = False
        # order or line depending on which view we are
        if purchase_order_id:
            apply_on = 'order'
            po_obj = self.pool.get('purchase.order')
            po = po_obj.browse(cr, uid, purchase_order_id, context=context)
            fiscal_position = po.fiscal_position or False
        else:
            apply_on = 'line'
        if not product_id:
            return res
        prod_obj = self.pool.get('product.product')
        dist_type_obj = self.pool.get('landed.cost.distribution.type')
        prod = prod_obj.browse(cr, uid, [product_id], context=context)[0]
        account_id = prod_obj._choose_exp_account_from(
            cr, uid, prod, fiscal_position=fiscal_position, context=context)
        if prod.landed_cost_type in ('per_unit', 'value'):
            landed_cost_type = dist_type_obj.search(
                cr, uid,
                [('apply_on', '=', apply_on),
                 ('landed_cost_type', '=', prod.landed_cost_type)],
                context=context)[0]
        value = {
            'distribution_type_id': landed_cost_type,
            'account_id': account_id,
            'partner_id': prod.seller_id and prod.seller_id.id or False
        }
        res = {'value': value}
        return res


class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"

    def _landing_cost(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'value' and
                            costs.distribution_type_id.apply_on == 'line'):
                        landed_costs += costs.amount
                    else:
                        landed_costs += costs.amount * line.product_qty
            result[line.id] = landed_costs
        return result

    def _landing_cost_order(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        lines = self.browse(cr, uid, ids,  context=context)
        # Landed costs line by line
        for line in lines:
            landed_costs = 0.0
            order = line.order_id
            # distribution of landed costs of PO
            if order.landed_cost_line_ids:
                # Base value (Absolute Value)
                if order.landed_cost_base_value:
                    try:
                        landed_costs += (order.landed_cost_base_value /
                                         order.amount_untaxed *
                                         line.price_subtotal)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        pass
                # Base quantity (Per Quantity)
                if order.landed_cost_base_quantity:
                    try:
                        landed_costs += (order.landed_cost_base_quantity /
                                         order.quantity_total *
                                         line.product_qty)
                    # We ignore the zero division error and doesn't sum
                    # matter of function filed computation order
                    except ZeroDivisionError:
                        pass
            result[line.id] = landed_costs
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        if not ids : return {}
        result = {}
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs = 0.0
            landed_costs += (line.price_subtotal +
                             line.landing_costs + line.landing_costs_order)
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


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    def _landed_cost_base_value(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_costs_base_value = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'value' and
                            costs.distribution_type_id.apply_on == 'order'):
                        landed_costs_base_value += costs.amount
            result[line.id] = landed_costs_base_value
        return result

    def _landed_cost_base_quantity(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_costs_base_quantity = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.landed_cost_line_ids:
                for costs in line.landed_cost_line_ids:
                    if (costs.distribution_type_id.landed_cost_type == 'per_unit' and
                            costs.distribution_type_id.apply_on == 'order'):
                         landed_costs_base_quantity += costs.amount
            result[line.id] = landed_costs_base_quantity
        return result

    def _quantity_total(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        quantity_total = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.order_line:
                for pol in line.order_line:
                    if pol.product_qty > 0.0:
                         quantity_total += pol.product_qty
            result[line.id] = quantity_total
        return result

    def _landed_cost(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_costs = 0.0
        # landed costs for the line
        for line in self.browse(cr, uid, ids, context=context):
            landed_costs += (line.landing_cost_lines +
                             line.landed_cost_base_value +
                             line.landed_cost_base_quantity +
                             line.amount_untaxed)
            result[line.id] = landed_costs
        return result

    def _landing_cost_lines(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        landed_cost_lines = 0.0
        for line in self.browse(cr, uid, ids, context=context):
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
            domain=[('purchase_order_line_id', '=', False)]),
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
        """ Here, the technical price_unit field will store the purchase
        price + landed cost. The original purchase price is stored in
        price_unit_net new field to keep record of it.

        """
        res = super(purchase_order,self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, context=context)
        res['price_unit_net'] =  res['price_unit']
        try:
            res['price_unit'] = order_line.landed_costs / order_line.product_qty
        except ZeroDivisionError:
            pass
        return res

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id,
                                      landed_cost, context=None):
        """ Collects require data from landed cost position that is used to
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
                landed_cost.distribution_type_id.landed_cost_type == 'per_unit'):
            qty = landed_cost.purchase_order_line_id.product_qty
        line_tax_ids = [x.id for x in landed_cost.product_id.supplier_taxes_id]
        return {
            'name': landed_cost.product_id.name,
            'account_id': account_id,
            'invoice_id' : inv_id,
            'price_unit': landed_cost.amount or 0.0,
            'quantity': qty,
            'product_id': landed_cost.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, line_tax_ids)],
        }

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        """ Collects require data from landed cost position that is used to
        create invoice for that particular position.

        Note that _landed can come from a line or at whole PO level.

        :param browse_record landed_cost: Landed cost position browse record
        :return: Value for fields of invoice.
        :rtype: dict

        """
        po = (landed_cost.purchase_order_id or
              landed_cost.purchase_order_line_id.order_id)
        currency_id = landed_cost.purchase_order_id.pricelist_id.currency_id.id
        fiscal_position_id = po.fiscal_position.id if po.fiscal_position else False
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(
            cr, uid,
            [('type', '=', 'purchase'),
             ('company_id', '=', po.company_id.id)],
            limit=1)
        if not journal_ids:
            raise orm.except_orm(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id: %d).')
                % (po.company_id.name, po.company_id.id))
        return {
            'currency_id': currency_id,
            'partner_id': landed_cost.partner_id.id,
            'account_id': landed_cost.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'origin': po.name,
            'fiscal_position': fiscal_position_id,
            'company_id': po.company_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
        }

    def _generate_invoice_from_landed_cost(self, cr, uid, landed_cost,
                                           context=None):
        """ Generate an invoice from order landed costs (means generic
        costs to a whole PO) or from a line landed costs.

        """
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        prod_obj = self.pool.get('product.product')
        po = (landed_cost.purchase_order_id or
              landed_cost.purchase_order_line_id.order_id)
        vals_inv = self._prepare_landed_cost_inv(cr, uid, landed_cost,
                                                 context=context)
        inv_id = invoice_obj.create(cr, uid, vals_inv, context=context)
        fiscal_position = (po.fiscal_position or False)
        exp_account_id = prod_obj._choose_exp_account_from(
            cr, uid,
            landed_cost.product_id,
            fiscal_position=fiscal_position,
            context=context
        )
        vals_line = self._prepare_landed_cost_inv_line(
            cr, uid, exp_account_id, inv_id,
            landed_cost, context=context
        )
        inv_line_id = invoice_line_obj.create(cr, uid, vals_line,
                                              context=context)
        return inv_id

    def wkf_approve_order(self, cr, uid, ids, context=None):
        """ On PO approval, generate all invoices for all landed cost position.

        Remember that only landed cost position with the checkbox
        generate_invoice ticked are generated.

        """
        res = super(purchase_order,self).wkf_approve_order(cr, uid, ids,
                                                           context=context)
        for order in self.browse(cr, uid, ids, context=context):
            invoice_ids = []
            for order_cost in order.landed_cost_line_ids:
                if order_cost.generate_invoice:
                    inv_id = self._generate_invoice_from_landed_cost(
                        cr, uid, order_cost, context=context)
                    invoice_ids.append(inv_id)
            for po_line in order.order_line:
                for line_cost in po_line.landed_cost_line_ids:
                    inv_id = self._generate_invoice_from_landed_cost(
                        cr, uid, line_cost, context=context)
                    invoice_ids.append(inv_id)
            # Link this new invoice to related purchase order
            # 4 in that list is "Add" mode in a many2many used here because
            # the call to super() already add the main invoice
            if invoice_ids:
                commands = [(4, invoice_id) for invoice_id in invoice_ids]
                order.write({'invoice_ids': commands}, context=context)
        return res
