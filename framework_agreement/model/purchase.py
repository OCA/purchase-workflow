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
from openerp.addons.framework_agreement.model.framework_agreement import FrameworkAgreementObservable


class purchase_order_line(orm.Model, FrameworkAgreementObservable):
    """Add on change on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    _columns = {'framework_agreement_id': fields.many2one('framework.agreement',
                                                          'Agreement')}

    def onchange_agreement(self, cr, uid, ids, agreement_id, qty,
                           date, product_id, pricelist_id, supplier_id, context=None):
        currency = self._currency_get(cr, uid, pricelist_id, context=context)
        return self.onchange_agreement_obs(cr, uid, ids, agreement_id, qty,
                                           date, product_id,
                                           currency=currency, price_field='price_unit')

    def onchange_price(self, cr, uid, ids, price, agreement_id, qty, pricelist_id, context=None):
        """Raise a warning if a agreed price is changed"""
        currency = self._currency_get(cr, uid, pricelist_id, context=context)
        return self.onchange_price_obs(cr, uid, ids, price, agreement_id, currency=currency,
                                       qty=qty, context=None)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False,
                            date_planned=False, name=False, price_unit=False,
                            context=None, **kwargs):
        """ We override this function to check qty change (I know...)

        The price retrieval is managed by the override of product.pricelist.price_get
        that is overidden to support agreement. We do this to avoid trouble with chained
        triggered on_change and ensure Make PO uses LTA
        This is mabye a faulty design as it has a low level impact

        """
        # rock n'roll
        res = super(purchase_order_line, self).onchange_product_id(
                cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
                date_planned=date_planned, name=name, price_unit=price_unit, context=context, **kwargs)

        currency = self._currency_get(cr, uid, pricelist_id, context=context)
        vals = self.onchange_quantity_obs(cr, uid, ids, qty, date_order,
                                          product_id, currency=currency,
                                          supplier_id=partner_id,
                                          price_field='price_unit',
                                          context=context)
        res['value'].update(vals.get('value', {}))
        if vals.get('warning'):
            res['warning'] = vals['warning']
        return res
