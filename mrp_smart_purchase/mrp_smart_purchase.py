# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2012 Camptocamp SA
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
from openerp.osv.orm import Model


class MrpProcurement(Model):

    """Mrp Procurement we override action_po assing to get the cheapest
    supplier, if you want to change priority parameters just change the
    _supplier_to_tuple function TODO remove hack if merge proposal accepted
    look in action_po_assing for details"""

    _inherit = "procurement.order"

    def action_po_assign(self, cursor, uid, ids, context=None):
        context = context or {}
        # stack is prduct id : qty
        # this is a hack beacause make_po hase no function
        # get supplier so I pass requiered data in context
        # I know that sucks but OpenEPR wont change this function in stable
        # relase Merge proposal for trunkis running
        context['smart_mrp_stack'] = {}
        for proc in self.browse(cursor, uid, ids, context):
            context['smart_mrp_stack'][proc.product_id.id] = proc.product_qty
        res = super(MrpProcurement, self).action_po_assign(
            cursor, uid, ids, context=context)
        return res


class ProductTemplate(Model):

    """ We overrride the get_main_supplier function
    that is used to retrieve supplier in function fields"""

    _name = "product.template"
    _inherit = "product.template"

    def _supplier_to_tuple(self, cursor, uid, supplier_id, price, product_id):
        """ Generate an tuple that can be sorted """
        # This is not the most performat way but it allows easy overriding
        # the faster solution will be to populate a mapping hash in
        # _get_main_product_supplier
        info_obj = self.pool.get('product.supplierinfo')
        info_id = info_obj.search(
            cursor, uid, [('product_id', '=', product_id),
                          ('name', '=', supplier_id)], order='sequence')[0]
        info = info_obj.browse(cursor, uid, info_id)
        res_tuple = (price, info.delay, info.sequence or 10000, info.id)
        return res_tuple

    def _get_main_product_supplier(self, cursor, uid, product, context=None):
        """Determines the main (best) product supplier for ``product``,
        using smart_mrp_stack in context to determine qty else it uses sequence
        """
        info_obj = self.pool.get('product.supplierinfo')
        context = context or {}
        smart_mrp_stack = context.get('smart_mrp_stack', {})
        if product.id in smart_mrp_stack:
            # we look for best prices based on supplier info
            sellers = product.seller_ids
            supplier_ids = [x.name.id for x in sellers]
            qty = smart_mrp_stack.get(product.id, 1)
            best_prices_persupplier = info_obj.price_get(
                cursor, uid, supplier_ids,
                product.id, qty, context=context)
            # Assmuption to sort price is more important than delay
            final_choice = []
            for supp, price in best_prices_persupplier.items():
                final_choice.append(
                    self._supplier_to_tuple(cursor, uid, supp, price,
                                            product.id))
            final_choice.sort()
            return info_obj.browse(cursor, uid, final_choice[0][3])
        else:
            return super(ProductTemplate, self)._get_main_product_supplier(
                cursor, uid, product, context)
        return False
