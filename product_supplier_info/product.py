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
import openerp.addons.decimal_precision as dp


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    def _product_available(
            self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {}.fromkeys(field_names, 0.0)
            for f in field_names:
                if f == 'qty_available':
                    res[record.id][f] = record.product_id.qty_available
                if f == 'virtual_available':
                    res[record.id][f] = record.product_id.virtual_available
        return res

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Product', select=1,
            ondelete='cascade', required=True),
        'qty_available': fields.function(
            _product_available, multi='qty_available', type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string="Quantity On Hand"),
        'virtual_available': fields.function(
            _product_available, multi='qty_available', type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string="Forecasted Quantity"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
