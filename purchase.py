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


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def add_product(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'only one record can be processed'
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        categ_obj = self.pool.get('product.category')

        result = mod_obj.get_object_reference(cr, uid,
                'quick_purchase_dd',
                'product_product_action')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        purchase = self.browse(cr, uid, ids[0], context=context)
        brand_ids = categ_obj.search(cr, uid, [
            ('supplier_id', '=', purchase.partner_id.id),
            ], context=context)

        domain = [
            ('categ_brand_id','in', brand_ids),
            ('is_display', '=', False),
            ('restocking_type', '=', purchase.restocking_type),
            ]
        result['domain'] = str(domain)
        context.update({
            'purchase_id': ids[0],
            'search_default_filter_to_sell': True,
            })
        result['context'] = context
        return result
