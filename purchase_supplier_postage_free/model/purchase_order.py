# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _compute_free_postage(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            supplier = order.partner_id
            order_currency = order.pricelist_id.currency_id
            amount = self._get_free_postage_amount(cr, uid, supplier,
                                                   order_currency,
                                                   context=context)
            res[order.id] = amount
        return res

    _columns = {
        'free_postage': fields.function(
            _compute_free_postage,
            string='Free Postage',
            digits_compute=dp.get_precision('Account'),
            help="Amount above which the supplier offers postage fees in the "
                 "currency of the purchase order,"
        ),
    }

    def _get_free_postage_amount(self, cr, uid, supplier, order_currency,
                                 context=None):
        currency_model = self.pool['res.currency']
        amount = supplier.free_postage
        supplier_pricelist = supplier.property_product_pricelist_purchase
        supplier_currency = supplier_pricelist.currency_id
        if supplier_currency != order_currency:
            amount = currency_model.compute(
                cr, uid,
                supplier_currency.id,
                order_currency.id,
                amount,
                context=context)
        return amount

    def onchange_partner_id(self, cr, uid, ids, partner_id, pricelist_id,
                            context=None):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids,
                                                              partner_id)
        if not pricelist_id or not partner_id:
            return res
        partner_model = self.pool['res.partner']
        pricelist_model = self.pool['product.pricelist']
        partner = partner_model.browse(cr, uid, partner_id,
                                       context=context)
        pricelist = pricelist_model.browse(cr, uid, pricelist_id,
                                           context=context)
        amount = self._get_free_postage_amount(
            cr, uid,
            partner,
            pricelist.currency_id,
            context=context)
        res.setdefault('value', {})['free_postage'] = amount
        return res

    def onchange_pricelist(self, cr, uid, ids, pricelist_id, context=None):
        res = super(purchase_order, self).onchange_pricelist(cr, uid, ids,
                                                             pricelist_id,
                                                             context=context)
        if not pricelist_id or not context.get('partner_id'):
            return res
        partner_model = self.pool['res.partner']
        pricelist_model = self.pool['product.pricelist']
        partner = partner_model.browse(cr, uid, context['partner_id'],
                                       context=context)
        pricelist = pricelist_model.browse(cr, uid, pricelist_id,
                                           context=context)
        amount = self._get_free_postage_amount(
            cr, uid,
            partner,
            pricelist.currency_id,
            context=context)
        res.setdefault('value', {})['free_postage'] = amount
        return res
