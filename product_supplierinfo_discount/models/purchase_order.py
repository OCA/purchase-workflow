# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import orm


class PurchaseOrderLine(orm.Model):
    _inherit = "purchase.order.line"

    def onchange_product_id(
            self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, context=None):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)
        if not product_id:
            return res
        supplierinfo_obj = self.pool['product.supplierinfo']
        product_obj = self.pool['product.product']
        product_uom_obj = self.pool['product.uom']
        pl_pinfo_obj = self.pool['pricelist.partnerinfo']
        # Look for a possible discount
        product = product_obj.browse(cr, uid, product_id, context=context)
        from_uom = context.get('uom') or product.uom_id.id
        qty_in_product_uom = qty
        sinfo_ids = supplierinfo_obj.search(
            cr, uid, [('product_id', '=', product.product_tmpl_id.id),
                      ('name', 'child_of', partner_id)], context=context)
        if not sinfo_ids:
            return res
        sinfo = supplierinfo_obj.browse(cr, uid, sinfo_ids[0], context=context)
        seller_uom = sinfo.product_uom.id or False
        if seller_uom and from_uom and from_uom != seller_uom:
            qty_in_product_uom = product_uom_obj._compute_qty(
                cr, uid, from_uom, qty, to_uom_id=seller_uom)
        pl_pinfo_ids = pl_pinfo_obj.search(
            cr, uid, [('suppinfo_id', 'in', sinfo_ids)], order="min_quantity")
        pl_pinfos = pl_pinfo_obj.read(
            cr, uid, pl_pinfo_ids, ['min_quantity', 'discount'])
        if 'value' not in res:
            res['value'] = {}
        for pl_pinfo in pl_pinfos:
            if pl_pinfo['min_quantity'] <= qty_in_product_uom:
                res['value']['discount'] = pl_pinfo['discount']
            else:
                break
        return res
