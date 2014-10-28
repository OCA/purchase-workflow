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
from openerp.osv import orm, fields
from openerp import models, fields as nfields, api
from openerp import exceptions, _


class purchase_order_line(orm.Model):
    """Add on change on price to raise a warning if line is subject to
    an agreement

    There is too munch conflict when overriding on change defined on old API
    With new API classes. This does not work
    """

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
            string='Agreement'
        )
    }

    def _currency_get(self, cr, uid, pricelist_id, context=None):
        """Retrieve pricelist currency"""
        return self.pool['product.pricelist'].browse(
            cr, uid,
            pricelist_id,
            context=context).currency_id

    def _onchange_price(self, cr, uid, ids, price, agreement_id,
                        currency=None, qty=0, context=None):
        """Raise a warning if a agreed price is changed on observed object"""
        if context is None:
            context = {}
        if not agreement_id or context.get('no_chained'):
            return {}
        agr_obj = self.pool['framework.agreement']
        agreement = agr_obj.browse(cr, uid, agreement_id, context=context)
        if agreement.get_price(qty, currency=currency) != price:
            msg = _(
                "You have set the price to %s \n"
                " but there is a running agreement"
                " with price %s") % (
                    price, agreement.get_price(qty, currency=currency)
            )
            raise exceptions.Warning(msg)
        return {}

    def onchange_price(self, cr, uid, ids, price, agreement_id,
                       qty, pricelist_id, product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        if not product_id or not agreement_id:
            return {}
        currency = self._currency_get(cr, uid, pricelist_id, context=context)
        product = self.pool['product.product'].browse(
            cr, uid, product_id, context=context)
        if product.type == 'service':
            return {}
        return self._onchange_price(cr, uid, ids, price,
                                    agreement_id, currency=currency,
                                    qty=qty, context=None)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id,
                            qty, uom_id, partner_id, date_order=False,
                            fiscal_position_id=False,
                            date_planned=False, name=False,
                            price_unit=False, state='draft', context=None):
        """ We override this function to check qty change (I know...)

        The price retrieval is managed by
        the override of product.pricelist.price_get

        that is overidden to support agreement.
        This is maybe a faulty design as it has a low level impact

        We use web_context_tunnel to keep the original signature.

        """
        agreement_id = context.get('agreement_id')
        # rock n'roll
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
            context=context
        )
        if not product_id or not agreement_id:
            return res
        product = self.pool['product.product'].browse(
            cr, uid,
            product_id,
            context=context
        )
        if product.type != 'service' and agreement_id:
            agreement = self.pool['framework.agreement'].browse(
                cr, uid,
                agreement_id,
                context=context
            )
            if agreement.product_id != product:
                raise exceptions.Warning(_('Product not in agreement'))
            currency = self._currency_get(
                cr, uid,
                pricelist_id,
                context=context
            )
            res['value']['price_unit'] = agreement.get_price(
                qty,
                currency=currency
            )
        return res


class purchase_order(models.Model):
    """Add on change to raise warning
    and add a relation to framework agreement"""

    _inherit = "purchase.order"

    framework_agreement_id = nfields.Many2one(
        'framework.agreement',
        'Agreement'
    )

    @api.model
    def _currency_get(self, pricelist_id):
        """Get a currency from a pricelist"""
        return self.env['product.pricelist'].browse(
            pricelist_id).currency_id

    @api.multi
    def _propagate_payment_term(self):
        if self.framework_agreement_id.payment_term_id:
            self.payment_term_id = self.framework_agreement_id.payment_term_id

    @api.onchange('framework_agreement_id')
    def onchange_agreement(self):
        res = {}

        self._propagate_payment_term()

        if isinstance(self.id, models.NewId):
            return res
        if self.framework_agreement_id:
            agreement = self.framework_agreement_id
            if not agreement.date_valid(self.date_order):
                raise exceptions.Warning(
                    _('Invalid date '
                      'Agreement and purchase date does not match')
                )
            if agreement.supplier_id.id != self.partner_id:
                raise exceptions.Warning(
                    _('Invalid agreement '
                      'Agreement and supplier does not match')
                )

            raise exceptions.Warning(
                _('Agreement Warning! '
                  'If you change the agreement of this order'
                  ' (and eventually the currency),'
                  ' existing order lines will not be updated.')
            )
        return res

    @api.multi
    def onchange_pricelist(self, pricelist_id):
        """We use web_context_tunnel to keep the original signature"""
        res = super(purchase_order, self).onchange_pricelist(
            pricelist_id,
        )
        if not pricelist_id or not self._context.get('order_line_ids'):
            return res
        if self.framework_agreement_id:
            raise exceptions.Warning(
                _('If you change the pricelist of this order'
                  ' (and eventually the currency),'
                  ' prices of existing order lines will not be updated.')
            )
        return res

    @api.model
    def _date_valid(self):
        """predicate that check that date of invoice is in agreement"""
        return self.framework_agreement_id.date_valid(self.date_order)

    @api.onchange('date_order')
    def onchange_date(self):
        """Check that date is in agreement bound"""
        if not self.framework_agreement_id:
            return {}
        if not self._date_valid(self.framework_agreement_id,
                                self.date_order):
            raise exceptions.Warning(
                _('Invalid date '
                  'Agreement and purchase date does not match')
            )
        return {}

    @api.multi
    def onchange_partner_id(self, partner_id):
        """Override to ensure that partner can not be changed if agreement.

        We use web_context_tunnel in order to keep the original signature.

        """
        res = super(purchase_order, self).onchange_partner_id(
            partner_id
        )
        if self._context.get('agreement_id'):
            raise exceptions.Warning(
                _('You cannot change the supplier: '
                  'the PO is linked to an agreement')
            )
        return res
