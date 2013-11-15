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
from openerp.tools.translate import _
from openerp.addons.framework_agreement.model.framework_agreement import FrameworkAgreementObservable


class purchase_order_line(orm.Model, FrameworkAgreementObservable):
    """Add on change on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    _columns = {'framework_agreement_id': fields.related('order_id',
                                                         'framework_agreement_id',
                                                         type='many2one',
                                                         readonly=True,
                                                         store=True,
                                                         relation='framework.agreement',
                                                         string='Agreement')}

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
        that is overidden to support agreement.
        This is mabye a faulty design as it has a low level impact

        """
        # rock n'roll

        res = super(purchase_order_line, self).onchange_product_id(
                cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
                date_planned=date_planned, name=name, price_unit=price_unit, context=context, **kwargs)
        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
        if product.type == 'product' and agreement_id:
            agreement = self.pool['framework.agreement'].browse(cr, uid,
                                                                agreement_id,
                                                                context=context)
            if agreement.product_id != product_id:
                return {'warning':  _('Non service Product not in agreement')}
            currency = self._currency_get(cr, uid, pricelist_id, context=context)
            res['value']['price_unit'] = agreement.price_get(qty, currency=currency)
        return res


class purchase_order(orm.Model):
    """Oveeride on change to raise warning"""

    _inherit = "purchase.order"

    _columns = {'framework_agreement_id': fields.many2one('framework.agreement',
                                                          'Agreement')}

    def onchange_agreement(self, cr, uid, ids, agreement_id, context=None):
        res = {}
        warning = {'title': _('Agreemnt Warning!'),
                   'message': _('If you change the agreement of this order'
                                ' (and eventually the currency),'
                                ' existing order lines will not be updated.')}
        res['warning'] = warning
        return res

    def onchange_pricelist(self, cr, uid, ids, pricelist_id, context=None):
        res = super(purchase_order, self).onchange_pricelist(cr, uid, ids, pricelist_id,
                                                             context=context)
        if not pricelist_id:
            return res


        warning = {'title': _('Pricelist Warning!'),
                   'message': _('If you change the pricelist of this order'
                                ' (and eventually the currency),'
                                ' prices of existing order lines will not be updated.')}
        res['warning'] = warning
        return res
