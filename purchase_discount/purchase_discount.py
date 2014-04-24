# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp

class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids):
            discount = line.discount or 0.0
            new_price_unit = line.price_unit * (1 - discount / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, new_price_unit,
                                        line.product_qty, line.product_id, 
                                        line.order_id.partner_id)
            currency = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, currency, taxes['total'])
        return res

    _columns = {
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', 
                                digits_compute=dp.get_precision('Account')),
    }

    _defaults = {
        'discount': 0.0,
    }

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)', 
         'Discount must be lower than 100%.'),
    ]


class purchase_order(orm.Model):
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            amount_taxed = amount_untaxed = 0.0
            currency = order.pricelist_id.currency_id
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                discount = line.discount or 0.0
                new_price_unit = line.price_unit * (1 - discount / 100.0)
                for c in tax_obj.compute_all(cr, uid, line.taxes_id,
                                             new_price_unit,
                                             line.product_qty,
                                             line.product_id.id,
                                             order.partner_id)['taxes']:
                    amount_taxed += c.get('amount', 0.0)
            val['amount_tax'] = cur_obj.round(cr, uid, currency, amount_taxed)
            val['amount_untaxed'] = cur_obj.round(cr, uid, currency,
                                                  amount_untaxed)
            val['amount_total'] = (val['amount_untaxed'] + val['amount_tax'])
            res[order.id] = val
        return res

    def _prepare_inv_line(self, cr, uid, account_id, order_line,
                            context=None):
        result = super(purchase_order, self)._prepare_inv_line(cr, uid,
                                                               account_id,
                                                               order_line,
                                                               context)
        result['discount'] = order_line.discount or 0.0
        return result

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids,
                                                                context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, method=True,
                digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
        'amount_untaxed': fields.function(_amount_all, 
            digits_compute= dp.get_precision('Account'), 
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", 
            track_visibility='always'),
        'amount_tax': fields.function(_amount_all, 
            digits_compute= dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, 
            digits_compute= dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),

    }


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.purchase_line_id:
            line = {'discount': move_line.purchase_line_id.discount}
            self.pool.get('account.invoice.line').write(cr,
                                                        uid,
                                                        [invoice_line_id],
                                                        line)
        return super(stock_picking, self)._invoice_line_hook(cr,
                                                             uid,
                                                             move_line,
                                                             invoice_line_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
