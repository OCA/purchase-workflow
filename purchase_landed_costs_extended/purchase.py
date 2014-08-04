# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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


class landed_cost_position(orm.Model):
    _inherit = 'landed.cost.position'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not partner_id:
            return {}
        partner = self.pool.get('res.partner').browse(
            cr, uid, partner_id, context=context)
        pricelist = partner.property_product_pricelist_purchase
        return {'value': {'currency_id': pricelist.currency_id.id}}

    def onchange_amount_currency(self, cr, uid, ids,
                                 amount_currency, currency_id,
                                 date_po, context=None):
        assert len(ids) < 2
        parent_currency_id = None
        if ids:
            landed_cost = self.browse(cr, uid, ids[0], context=context)
            parent_currency_id = landed_cost.po_currency_id.id
        else:
            parent_currency_id = self._default_currency(
                cr, uid, context=context)
        if not parent_currency_id or not amount_currency or not currency_id:
            return {}
        cur_obj = self.pool.get('res.currency')
        amount = amount_currency
        if currency_id != parent_currency_id:
            ctx = context.copy()
            ctx['date'] = date_po or False
            amount = cur_obj.compute(cr, uid,
                                     currency_id,
                                     parent_currency_id,
                                     amount,
                                     context=ctx)
        return {'value': {'amount': amount}}

    def _default_currency(self, cr, uid, context=None):
        context = context or {}
        pricelist_id = context.get('pricelist_id', [])
        pricelist = self.pool.get('product.pricelist').read(
            cr, uid, pricelist_id, ['currency_id'])
        parent_currency_id = None
        if pricelist:
            parent_currency_id = pricelist['currency_id'][0]
        return parent_currency_id

    _columns = {
        'amount_currency': fields.float(
            'Currency Amount',
            digits_compute=dp.get_precision('Purchase Price'),
            help="Landed cost expressed in Landed Cost line currency"),
        'currency_id': fields.many2one(
            'res.currency', 'Currency'),
        'po_pricelist_id': fields.related(
            'purchase_order_id', 'pricelist_id',
            type='many2one',
            relation='product.pricelist',
            string='PO Pricelist',
            store=True,
            readonly=True,
            help="PO pricelist"),
        'po_currency_id': fields.related(
            'po_pricelist_id', 'currency_id',
            type='many2one',
            relation='res.currency',
            string='PO Currency',
            store=True,
            readonly=True,
            help="PO Currency"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'active': fields.boolean('Active')
    }

    _defaults = {
        'currency_id': _default_currency,
        'active': True
    }

    def open_invoice(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        lcp = self.browse(cr, uid, ids[0], context=context)
        if not lcp.invoice_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Form heading',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': lcp.invoice_id.id,
            'context': context
        }


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _generate_invoice_from_landed_cost(self, cr, uid, landed_cost,
                                           context=None):
        if landed_cost.invoice_id:
            return landed_cost.invoice_id.id
        inv_id = super(
            purchase_order, self
        )._generate_invoice_from_landed_cost(
            cr, uid, landed_cost, context=context)
        landed_cost.write({'invoice_id': inv_id}, context=context)
        return inv_id

    def _prepare_landed_cost_inv_line(self, cr, uid, account_id, inv_id,
                                      landed_cost, context=None):
        res = super(purchase_order, self)._prepare_landed_cost_inv_line(
            cr, uid, account_id, inv_id, landed_cost, context=context)
        res['price_unit'] = landed_cost.amount_currency
        return res

    def _prepare_landed_cost_inv(self, cr, uid, landed_cost, context=None):
        res = super(purchase_order, self)._prepare_landed_cost_inv(
            cr, uid, landed_cost, context=context)
        res['currency_id'] = landed_cost.currency_id.id
        return res

    def wkf_approve_order(self, cr, uid, ids, context=None):
        """ On PO approval, generate all invoices for all landed cost position.

        Remember that only landed cost position with the checkbox
        generate_invoice ticked are generated.

        """
        lcp_pool = self.pool.get('landed.cost.position')
        line_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            for po_line in order.order_line:
                for line_cost in po_line.landed_cost_line_ids:
                    if not line_cost.generate_invoice or line_cost.invoice_id:
                        line_ids = line_cost.id
        lcp_pool.write(cr, uid, line_ids, {'active': False})

        res = super(purchase_order, self).wkf_approve_order(cr, uid, ids,
                                                            context=context)
        lcp_pool.write(cr, uid, line_ids, {'active': True})
        return res
