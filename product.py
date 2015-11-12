# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


# WARNING FOR NOW WE DO NO TAKE IN ACCOUNT THE UOM BE CAREFULL
# WE ASSUME THAT THE UOM IS ALWAYS THE "UNIT"
# This module should be review in order to do something generic
# need customer investissement
class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _prepare_purchase_line(self, cr, uid, po, product_id, qty,
                              context=None):
        model_data_obj = self.pool['ir.model.data']
        po_line_obj = self.pool['purchase.order.line']
        __, uom_id = model_data_obj.get_object_reference(
            cr, uid, 'product', 'product_uom_unit')

        onchange_vals = po_line_obj.onchange_product_id(
            cr, uid, None, po.pricelist_id.id, product_id, qty, uom_id,
            po.partner_id.id, po.date_order, po.fiscal_position.id,
            date_planned=False, name=False, price_unit=False, context=context)

        vals = onchange_vals['value']
        vals.update({
            'taxes_id': [(6, 0, vals['taxes_id'])],
            'product_id': product_id,
            'product_qty': qty,
            'order_id': po.id,
            })
        return vals

    def _get_purchase_line(self, cr, uid, po_id, product_id, context=None):
        line_ids = self.pool['purchase.order.line'].search(cr, uid, [
            ('product_id', '=', product_id),
            ('order_id', '=', po_id),
            ], context=context)
        return line_ids[0] if line_ids else None

    def _add_purchase_line(self, cr, uid, po_id, product_id, qty,
                           context=None):
        po_obj = self.pool['purchase.order']
        po_line_obj = self.pool['purchase.order.line']
        po = po_obj.browse(cr, uid, po_id, context=context)
        vals = self._prepare_purchase_line(
            cr, uid, po, product_id, qty, context=context)
        po_line_obj.create(cr, uid, vals, context=context)
        return True

    def _update_purchase_line(self, cr, uid, line_id, qty, context=None):
        po_line_obj = self.pool['purchase.order.line']
        if qty:
            po_line_obj.write(cr, uid, [line_id], {
                'product_qty': qty,
                }, context=context)
        else:
            po_line_obj.unlink(cr, uid, [line_id], context=context)
        return True

    def _set_purchase_qty(self, cr, uid, id, name, value,
                          args=None, context=None):
        product = self.browse(cr, uid, id, context=context)
        if -product.immediately_usable_qty > value:
            raise orm.except_orm(
                _('User Error'),
                _('You can not order less then %s product,'
                  'as customer already buy it')
                % -product.immediately_usable_qty)
        po_id = context['purchase_id']
        po_line_id = self._get_purchase_line(cr, uid, po_id, product.id)
        if po_line_id:
            self._update_purchase_line(
                cr, uid, po_line_id, value, context=context)
        else:
            self._add_purchase_line(
                cr, uid, po_id, product.id, value, context=context)
        return True

    def _get_purchase_qty(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {product_id: 0 for product_id in ids}
        if not context.get('purchase_id'):
            return res
        po_line_obj = self.pool['purchase.order.line']
        po_line_ids = po_line_obj.search(cr, uid, [
            ('order_id', '=', context['purchase_id']),
            ('product_id', 'in', ids),
            ], context=context)
        for po_line in po_line_obj.browse(
                cr, uid, po_line_ids, context=context):
            res[po_line.product_id.id] += po_line.product_qty
        return res

    #TODO for V8 we should have a generic module that compute this value
    def _get_real_incomming_qty(self, cr, uid, ids, field_name,
                                args, context=None):
        res = {}
        model_data_obj = self.pool['ir.model.data']
        __, location_dest_id = model_data_obj.get_object_reference(
            cr, uid, 'stock', 'stock_location_stock')
        __, location_id = model_data_obj.get_object_reference(
            cr, uid, 'stock', 'stock_location_suppliers')

        cr.execute(
            """SELECT product_id, sum(product_qty)
            FROM stock_move
            WHERE location_id = %s
                AND location_dest_id = %s
                AND product_id IN %s
                AND state not in ('cancel', 'done')
            GROUP BY product_id, product_uom""",
            (location_id, location_dest_id, tuple(ids)))
        for product_id, qty in cr.fetchall():
            res[product_id] = qty
        for product_id in ids:
            if not product_id in res:
                res[product_id] = 0
        return res

    _columns = {
        'purchase_qty': fields.function(
            _get_purchase_qty,
            fnct_inv=_set_purchase_qty,
            string='Purchase QTY',
            type='integer'),
        'real_incomming_qty': fields.function(
            _get_real_incomming_qty,
            string='Incomming QTY',
            type='integer'),
        }
