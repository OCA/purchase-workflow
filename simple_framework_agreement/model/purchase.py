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
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.simple_framework_agreement.model.framework_agreement import FrameworkAgreementObservable

class purchase_order_line(orm.Model, FrameworkAgreementObservable):
    """Add on change on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    def onchange_price(self, cr, uid, ids, price, date, supplier_id, product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        return self.onchange_price_obs(cr, uid, ids, price, date, supplier_id,
                                       product_id, context=None)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False,
                            date_planned=False, name=False, price_unit=False,
                            state='draft', context=None):
        """ We override this function to check qty change (I know...)
        The price retrieval is managed by the override of product.pricelist.price_get
        that is overiden to support agreement. We do thios to avoid touble with chained
        triggered on change... and ensure Make Po use LTA this is mabye a faulty design"""
        # rock n'roll
        res = super(purchase_order_line, self).onchange_product_id(
                cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
                date_planned=date_planned, name=name, price_unit=price_unit,
                state=state, context=context
        )
        if qty:
            warning = self.onchange_quantity_obs(cr, uid, ids, qty, date_order, partner_id,
                                                 product_id, context)
            res.update(warning)
        return res

    def onchange_quantity(self, cr, uid, ids, qty, date, supplier_id, product_id, context=None):
        """Raise a warning if agreed qty is not sufficient"""
        return self.onchange_quantity_obs(cr, uid, ids, qty, date,
                                          supplier_id, product_id, context=context)
