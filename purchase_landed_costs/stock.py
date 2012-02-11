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

import math
#from _common import rounding
import re  
from tools.translate import _
import sys
import netsvc


#----------------------------------------------------------
#  Account Invoice Line INHERIT
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    def _get_price_unit_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('product_id', False):
            return False 
        pu_id = self.pool.get('product.product').browse(cr, uid, context['product_id']).price_unit_id.id
        return pu_id or False


    _columns = { 
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit'),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Sale Price'),  \
                            help='Price using "Price Units"') ,
        'price_unit'       : fields.float(string='Unit Price internal',  digits=(16, 8), \
                            help="""Product's cost for accounting stock valuation."""),
        'price_unit_sale'  : fields.float(string='Unit Price Sale',  digits=(16, 8), \
                            help="""Product's sale for accounting stock valuation."""),

        'price_unit_sale_id' : fields.many2one('c2c_product.price_unit','Price Unit Sale'),
        'price_unit_coeff':fields.float(string='Price/Coeff internal',digits=(16,8) ),

    }

    _defaults = {
        'price_unit_id'   : _get_price_unit_id,
#        'price_unit_pu'   : _get_price_unit_pu,
#        'price_unit'      : _get_price_unit,
    }

    def init(self, cr):
      cr.execute("""
          update stock_move set price_unit_pu = price_unit  where price_unit_pu is null;
      """)
      cr.execute("""
          update stock_move set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
      """)

    def onchange_price_unit(self, cr, uid, ids, field_name,price_pu, price_unit_id):
        if  price_pu and  price_unit_id:
           pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, price_unit_id)
           price = price_pu / float(pu.coefficient)
           return {'value': {field_name : price}}
        return {}
        
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        context = {}
        res = super(stock_move,self).onchange_product_id( cr, uid, ids, prod_id, loc_id,
                            loc_dest_id, address_id)
        if prod_id :
            prod_obj = self.pool.get('product.product').browse(cr, uid, prod_id)
            pu_id = prod_obj.price_unit_id.id
            standard_price_pu = prod_obj.standard_price_pu
            res['value'].update({'price_unit_id':pu_id, 'price_unit_pu':standard_price_pu})
        return res
      

stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"


    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        #res = super(stock_picking,self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)
        logger = netsvc.Logger()
        logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO,'price unit stock line hook FGF:  %s '%(invoice_line_id))
        price_unit_id = ''
        price_unit_pu = ''
        if move_line.price_unit_id:
            price_unit_id =  move_line.price_unit_id.id
        if move_line.price_unit_pu:
            price_unit_pu =  move_line.price_unit_pu
        if not price_unit_id or not price_unit_pu:
         if move_line.purchase_line_id:
          if not move_line.price_unit_id:
            price_unit_id = self.pool.get('c2c_product.price_unit').get_default_id(cr, uid, None)
          else:
            price_unit_id = move_line.price_unit_id.id
          coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
          print >> sys.stderr,'price_unit invoice_line-hook coeff:', coeff
          price_unit_pu = move_line.price_unit_pu or move_line.price_unit * coeff or ''
         if move_line.sale_line_id:
          price_unit = move_line.price_unit or ''
          price_unit_pu = move_line.price_unit or ''
          price_unit_id = move_line.price_unit_id.id or ''
          
        inv_line_obj = self.pool.get('account.invoice.line')
        inv_line_obj.write(cr, uid, invoice_line_id, {'price_unit_id': price_unit_id, 'price_unit_pu': price_unit_pu})

        return  super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)

    def action_invoice_create_nok(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        address_obj = self.pool.get('res.partner.address')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            payment_term_id = False
            partner =  picking.address_id and picking.address_id.partner_id
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if inv_type in ('out_invoice', 'out_refund'):
                account_id = partner.property_account_receivable.id
                payment_term_id = self._get_payment_term(cr, uid, picking)
            else:
                account_id = partner.property_account_payable.id

            address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cr, uid, picking).values()
            address = address_obj.browse(cr, uid, address_contact_id, context=context)

            comment = self._get_comment_invoice(cr, uid, picking)
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or '') + ', ' + (picking.name or ''),
                    'origin': (invoice.origin or '') + ', ' + (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'comment': (comment and (invoice.comment and invoice.comment+"\n"+comment or comment)) or (invoice.comment and invoice.comment or ''),
                    'date_invoice':context.get('date_inv',False),
                    'user_id':uid
                }
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': picking.name,
                    'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'type': inv_type,
                    'account_id': account_id,
                    'partner_id': address.partner_id.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'comment': comment,
                    'payment_term': payment_term_id,
                    'fiscal_position': partner.property_account_position.id,
                    'date_invoice': context.get('date_inv',False),
                    'company_id': picking.company_id.id,
                    'user_id':uid
                }
                cur_id = self.get_currency_id(cr, uid, picking)
                if cur_id:
                    invoice_vals['currency_id'] = cur_id
                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cr, uid, invoice_vals,
                        context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                origin = move_line.picking_id.name or ''
                if move_line.picking_id.origin:
                    origin += ':' + move_line.picking_id.origin
                if group:
                    name = (picking.name or '') + '-' + move_line.name
                else:
                    name = move_line.name

                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_income.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_income_categ.id
                else:
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_expense.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_expense_categ.id

                price_unit = self._get_price_unit_invoice(cr, uid,
                        move_line, inv_type)
                # FIXME        
                price_unit_id = self.pool.get('c2c_product.price_unit').get_default_id(cr, uid, move_line.price_unit_id.id) 
                coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)        
                price_unit_pu = price_unit * coeff        
                discount = self._get_discount_invoice(cr, uid, move_line)
                tax_ids = self._get_taxes_invoice(cr, uid, move_line, inv_type)
                account_analytic_id = self._get_account_analytic_invoice(cr, uid, picking, move_line)

                #set UoS if it's a sale and the picking doesn't have one
                uos_id = move_line.product_uos and move_line.product_uos.id or False
                if not uos_id and inv_type in ('out_invoice', 'out_refund'):
                    uos_id = move_line.product_uom.id

                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
                
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': move_line.product_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'price_unit_pu': price_unit_pu,
                    'price_unit_id': price_unit_id,
                    'discount': discount,
                    'quantity': move_line.product_uos_qty or move_line.product_qty,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_analytic_id': account_analytic_id,
                }, context=context)
                self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res
stock_picking()


