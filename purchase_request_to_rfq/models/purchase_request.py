# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta

_PURCHASE_ORDER_LINE_STATE = [
    ('none', 'No Purchase'),
    ('draft', 'RFQ'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')
]


class PurchaseRequestLine(orm.Model):

    _inherit = "purchase.request.line"

    def _get_is_editable(self, cr, uid, ids, names, arg, context=None):
        res = super(PurchaseRequestLine, self)._get_is_editable(
            cr, uid, ids, names, arg, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            if line.purchase_lines:
                res[line.id] = False
        return res

    def _purchased_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for request_line in self.browse(cr, uid, ids, context=context):
            purchased_qty = 0.0
            for purchase_line in request_line.purchase_lines:
                if purchase_line.state != 'cancel':
                    purchased_qty += purchase_line.product_qty
            res[request_line.id] = purchased_qty
        return res

    def _get_purchase_state(self, cr, uid, ids, names, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 'none'
            if any([po_line.state == 'done' for po_line in
                    line.purchase_lines]):
                res[line.id] = 'done'
            elif all([po_line.state == 'cancel' for po_line in
                      line.purchase_lines]):
                res[line.id] = 'cancel'
            elif any([po_line.state == 'confirmed' for po_line in
                      line.purchase_lines]):
                res[line.id] = 'confirmed'
            elif all([po_line.state in ('draft', 'cancel') for po_line in
                      line.purchase_lines]):
                res[line.id] = 'draft'
        return res

    def _get_request_lines_from_po(self, cr, uid, ids, context=None):
        request_line_ids = []
        for order in self.pool['purchase.order'].browse(
                cr, uid, ids, context=context):
            for line in order.order_line:
                for request_line in line.purchase_request_lines:
                    request_line_ids.append(request_line.id)
        return list(set(request_line_ids))

    def _get_request_lines_from_po_lines(self, cr, uid, ids, context=None):
        request_line_ids = []
        for order_line in self.pool['purchase.order.line'].browse(
                cr, uid, ids, context=context):
            for request_line in order_line.purchase_request_lines:
                request_line_ids.append(request_line.id)
        return list(set(request_line_ids))

    _columns = {
        'purchased_qty': fields.function(_purchased_qty,
                                         string='Quantity in RFQ or PO',
                                         type='float'),
        'purchase_lines': fields.many2many(
            'purchase.order.line',
            'purchase_request_purchase_order_line_rel',
            'purchase_request_line_id',
            'purchase_order_line_id',
            'Purchase Order Lines', readonly=True),
        'purchase_state': fields.function(
            _get_purchase_state, string="Purchase Status",
            type="selection",
            selection=_PURCHASE_ORDER_LINE_STATE,
            store={
                'purchase.order': (
                    _get_request_lines_from_po,
                    ['state', 'order_line'], 10),
                'purchase.order.line': (
                    _get_request_lines_from_po_lines,
                    ['state', 'purchase_request_lines'], 10)}),

        'is_editable': fields.function(_get_is_editable,
                                       string="Is editable",
                                       type="boolean")
    }

    _defaults = {
        'purchase_state': 'none',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'purchase_lines': [],
        })
        return super(PurchaseRequestLine, self).copy(
            cr, uid, id, default, context)

    def _planned_date(self, request_line, delay=0.0):
        company = request_line.company_id
        date_planned = datetime.strptime(
            request_line.date_required, '%Y-%m-%d') - \
            relativedelta(days=company.po_lead)
        if delay:
            date_planned -= relativedelta(days=delay)
        return date_planned and date_planned.strftime('%Y-%m-%d') \
            or False

    def _seller_details(self, cr, uid, request_line, product,
                        product_qty, product_uom, supplier,
                        context=None):
        product_uom_obj = self.pool['product.uom']
        pricelist_obj = self.pool['product.pricelist']
        default_uom_po_id = product.uom_po_id.id
        qty = product_uom_obj._compute_qty(cr, uid,
                                           product_uom.id,
                                           product_qty,
                                           default_uom_po_id)
        seller_delay = 0.0
        seller_qty = False
        for product_supplier in product.seller_ids:
            if supplier.id == product_supplier.name \
                    and qty >= product_supplier.qty:
                seller_delay = product_supplier.delay
                seller_qty = product_supplier.qty
        supplier_pricelist = supplier.property_product_pricelist_purchase \
            or False
        seller_price = pricelist_obj.price_get(
            cr, uid, [supplier_pricelist.id],
            product.id, qty, supplier.id,
            {'uom': default_uom_po_id})[supplier_pricelist.id]
        if seller_qty:
            qty = max(qty, seller_qty)
        date_planned = self._planned_date(request_line,
                                          seller_delay)
        return seller_price, qty, default_uom_po_id, date_planned

    def _calc_new_qty_price(self, cr, uid, request_line,
                            po_line=None,
                            cancel=False, context=None):
        uom_obj = self.pool.get('product.uom')
        qty = uom_obj._compute_qty(cr, uid, request_line.product_uom_id.id,
                                   request_line.product_qty,
                                   request_line.product_id.uom_po_id.id)
        # Make sure we use the minimum quantity of the partner corresponding
        # to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if po_line.order_id.location_id.usage != 'customer':
            if po_line.product_id.seller_id.id == \
                    po_line.order_id.partner_id.id:
                supplierinfo_min_qty = po_line.product_id.seller_qty
            else:
                supplierinfo_obj = self.pool['product.supplierinfo']
                supplierinfo_ids = supplierinfo_obj.search(
                    cr, uid, [('name', '=', po_line.order_id.partner_id.id),
                              ('product_id', '=',
                               po_line.product_id.id)], context=context)
                if supplierinfo_ids:
                    supplierinfo_min_qty = supplierinfo_obj.browse(
                        cr, uid, supplierinfo_ids[0], context=context).min_qty

        if supplierinfo_min_qty == 0.0:
            qty += po_line.product_qty
        else:
            # Recompute quantity by adding existing running procurements.
            for rl in po_line.purchase_request_lines:
                qty += uom_obj._compute_qty(cr, uid, rl.product_uom_id.id,
                                            rl.product_qty,
                                            rl.product_id.uom_po_id.id)
            qty = max(qty, supplierinfo_min_qty) if qty > 0.0 else 0.0

        price = po_line.price_unit
        if qty != po_line.product_qty:
            pricelist_obj = self.pool['product.pricelist']
            pricelist_id = po_line.order_id.partner_id.\
                property_product_pricelist_purchase.id
            price = pricelist_obj.price_get(
                cr, uid, [pricelist_id], request_line.product_id.id, qty,
                po_line.order_id.partner_id.id,
                {'uom': request_line.product_id.uom_po_id.id})[pricelist_id]

        return qty, price

    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.purchase_lines:
                raise orm.except_orm(
                    _('Error!'),
                    _('You cannot delete a record that refers to purchase '
                      'lines!'))
        return super(PurchaseRequestLine, self).unlink(cr, uid, ids,
                                                       context=context)
