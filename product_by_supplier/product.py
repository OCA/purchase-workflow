# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it wil    l be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    def _product_available(
            self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or {}
        res = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {}
            product = product_obj.browse(
                cr, uid, record.product_id.id, context=context)
            res[record.id]['qty_available'] = product.qty_available
            res[record.id]['virtual_available'] = product.virtual_available
        return res

    _columns = {
        # It cannot be done with related fields because product_id points to
        # product.template, not product.product
        'qty_available': fields.function(
            _product_available, multi='qty_available', type='float',
            string="Quantity On Hand"),
        'virtual_available': fields.function(
            _product_available, multi='virtual_available', type='float',
            string="Forecasted Quantity"),
        'delay': fields.integer(
            'Delivery Lead Time', required=True, group_operator="avg",
            help="Lead time in days between the confirmation of the"
            " purchase order and the reception of the products in your"
            " warehouse. Used by the scheduler for automatic computation of"
            " the purchase order planning."
        ),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
