# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013, 2014 Camptocamp SA
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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import orm, fields


# Using new API seem to have side effect on
# other official addons
class product_pricelist(orm.Model):

    """Add framework agreement behavior on pricelist"""

    _inherit = "product.pricelist"

    def _plist_is_agreement(self, cr, uid, pricelist_id, context=None):
        """Check that a price list can be subject to agreement.

        :param pricelist_id: the price list to be validated

        :returns: a boolean (True if agreement is applicable)

        """
        p_list = self.browse(cr, uid, pricelist_id, context=context)
        return p_list.type == 'purchase'

    def price_get(self, cr, uid, ids, prod_id, qty,
                  partner=None, context=None):
        """Override of price retrieval function in order to support framework
        agreement.

        If it is a supplier price list, agreement will be taken in account
        and use the price of the agreement if required.

        If there is not enough available qty on agreement,
        standard price will be used.

        This is maybe a faulty design and we should use on_change override

        """
        if context is None:
            context = {}
        agreement_obj = self.pool['framework.agreement']
        res = super(product_pricelist, self).price_get(
            cr, uid, ids, prod_id, qty, partner=partner, context=context)
        if not partner:
            return res
        for pricelist_id in res:
            if (pricelist_id == 'item_id' or not
                    self._plist_is_agreement(cr, uid,
                                             pricelist_id, context=context)):
                continue
            now = datetime.strptime(fields.date.today(),
                                    DEFAULT_SERVER_DATE_FORMAT)
            date = context.get('date') or context.get('date_order') or now
            prod = self.pool['product.product'].browse(cr, uid, prod_id,
                                                       context=context)
            agreement = agreement_obj.get_product_agreement(
                cr, uid,
                prod.product_tmpl_id.id,
                partner,
                date,
                qty=qty,
                context=context
            )
            if agreement is not None:
                currency = agreement_obj._get_currency(
                    cr, uid, partner, pricelist_id,
                    context=context
                )
                res[pricelist_id] = agreement.get_price(qty, currency=currency)
        return res
