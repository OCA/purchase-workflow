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
from openerp.addons.framework_agreement.model.framework_agreement \
    import FrameworkAgreementObservable


class purchase_order_line(orm.Model, FrameworkAgreementObservable):

    """Add on change on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    def _get_po_store(self, cr, uid, ids, context=None):
        res = set()
        po_obj = self.pool.get('purchase.order')
        for row in po_obj.browse(cr, uid, ids, context=context):
            res.update([x.id for x in row.order_line])
        return res

    def _get_po_line_store(self, cr, uid, ids, context=None):
        return ids

    _store_tuple = (_get_po_store, ['framework_agreement_id'], 20)
    _line_store_tuple = (_get_po_line_store, [], 20)

    _columns = {
        'framework_agreement_id': fields.related(
            'order_id',
            'framework_agreement_id',
            type='many2one',
            readonly=True,
            store={'purchase.order': _store_tuple,
                   'purchase.order.line': _line_store_tuple},
            relation='framework.agreement',
            string='Agreement')}

    def onchange_price(self, cr, uid, ids, price, agreement_id, qty,
                       pricelist_id, product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        if not product_id or not agreement_id:
            return {}
        currency = self._currency_get(cr, uid, pricelist_id, context=context)
        product = self.pool['product.product'].browse(
            cr, uid, product_id, context=context)
        if product.type == 'service':
            return {}
        return self.onchange_price_obs(cr, uid, ids, price, agreement_id,
                                       currency=currency, qty=qty,
                                       context=None)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, context=None,
                            agreement_id=False, **kwargs):
        """ We override this function to check qty change (I know...)

        The price retrieval is managed by the override of
        product.pricelist.price_get that is overidden to support agreement.
        This is mabye a faulty design as it has a low level impact

        """
        # rock n'roll
        if context is None:
            context = {}
        if agreement_id:
            context['from_agreement_id'] = agreement_id
        res = super(purchase_order_line, self).onchange_product_id(
            cr,
            uid,
            ids,
            pricelist_id,
            product_id,
            qty,
            uom_id,
            partner_id,
            date_order=date_order,
            fiscal_position_id=fiscal_position_id,
            date_planned=date_planned,
            name=name,
            price_unit=price_unit,
            context=context,
            **kwargs)
        if not product_id or not agreement_id:
            return res
        product = self.pool['product.product'].browse(
            cr, uid, product_id, context=context)
        if product.type != 'service' and agreement_id:
            agreement = self.pool['framework.agreement'].browse(
                cr, uid,
                agreement_id,
                context=context)
            if agreement.product_id.id != product_id:
                return {'warning':  _('Product not in agreement')}
            currency = self._currency_get(
                cr, uid, pricelist_id, context=context)
            res['value']['price_unit'] = agreement.get_price(
                qty, currency=currency)
        return res


class purchase_order(orm.Model):

    """Oveeride on change to raise warning"""

    _inherit = "purchase.order"

    _columns = {
        'framework_agreement_id': fields.many2one('framework.agreement',
                                                  'Agreement')}

    def onchange_agreement(self, cr, uid, ids, agreement_id, partner_id, date,
                           context=None):
        res = {}
        agr_obj = self.pool['framework.agreement']
        if agreement_id:
            agreement = agr_obj.browse(cr, uid, agreement_id, context=context)
            if not agreement.date_valid(date, context=context):
                raise orm.except_orm(
                    _('Invalid date'),
                    _('Agreement and purchase date does not match'))
            if agreement.supplier_id.id != partner_id:
                raise orm.except_orm(
                    _('Invalid agreement'),
                    _('Agreement and supplier does not match'))

        warning = {'title': _('Agreement Warning!'),
                   'message': _('If you change the agreement of this order'
                                ' (and eventually the currency),'
                                ' existing order lines will not be updated.')}
        res['warning'] = warning
        return res

    def onchange_pricelist(self, cr, uid, ids, pricelist_id, line_ids,
                           context=None):
        res = super(purchase_order, self).onchange_pricelist(cr, uid, ids,
                                                             pricelist_id,
                                                             context=context)
        if not pricelist_id or not line_ids:
            return res

        warning = {
            'title': _('Pricelist Warning!'),
            'message': _(
                'If you change the pricelist of this order'
                ' (and eventually the currency),'
                ' prices of existing order lines will not be updated.')}
        res['warning'] = warning
        return res

    def _date_valid(self, cr, uid, agreement_id, date, context=None):
        """predicate that check that date of invoice is in agreement"""
        agr_model = self.pool['framework.agreement']
        return agr_model.date_valid(cr, uid, agreement_id, date,
                                    context=context)

    def onchange_date(self, cr, uid, ids, agreement_id, date, context=None):
        """Check that date is in agreement"""
        if agreement_id and not self._date_valid(cr, uid, agreement_id, date,
                                                 context=context):
            raise orm.except_orm(
                _('Invalid date'),
                _('Agreement and purchase date does not match'))
        return {}

    # no context in original def...
    def onchange_partner_id(self, cr, uid, ids, partner_id, agreement_id):
        """Override to ensure that partner can not be changed if agreement"""
        res = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id)
        if agreement_id:
            raise orm.except_orm(_('You can not change supplier'),
                                 _('PO is linked to an agreement'))
        return res
