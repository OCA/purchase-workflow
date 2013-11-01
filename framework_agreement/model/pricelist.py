# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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


class product_pricelist(orm.Model):
    """Add framework agreement behavior on pricelist"""

    _inherit = "product.pricelist"

    def _plist_is_agreement(self, cr, uid, pricelist_id, context=None):
        """Check that a price list can be subject to LTA
        :param pricelist_id: the price list to be validated
        :returns: a boolean (True if aggrement is applicable)"""
        p_list = self.browse(cr, uid, pricelist_id, context=context)
        if p_list.type == 'purchase':
            return True
        return False

    def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        """Override of price retrival function in order to support framework agreement.
        If it is a supplier price list lta will be taken in account and take the price of the
        agreement if required if there is not enought available qty on lta
        standard price will be used. This is mabye a faulty design and we should
        use on change override"""
        agreement_obj = self.pool['framework.agreement']
        res = super(product_pricelist, self).price_get(cr, uid, ids, prod_id, qty,
                                                       partner=partner, context=context)
        if not partner:
            return res
        for pricelist_id in res:
            if (pricelist_id == 'item_id' or not
                    self._plist_is_agreement(cr, uid, pricelist_id, context=context)):
                continue

            now = fields.datetime.now()
            date = context.get('date') or context.get('date_order') or now
            agreement = agreement_obj.get_product_agreement(cr, uid, prod_id,
                                                      partner, date,
                                                      qty=qty, context=context)

            if agreement is not None:
                res[pricelist_id] = agreement.get_price(qty)
        return res
