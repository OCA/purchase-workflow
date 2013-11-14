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
from operator import attrgetter
from collections import namedtuple
from datetime import datetime
from openerp.osv import orm, fields
from openerp.osv.orm import except_orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

AGR_PO_STATE = ('confirmed', 'approved',
                'done', 'except_picking', 'except_invoice')


class framework_agreement(orm.Model):
    """Long term agreement on product price with a supplier"""

    _name = 'framework.agreement'
    _description = 'Agreement on price'

    def _check_running_date(self, cr, agreement, context=None):
        """ Returns agreement state based on date.

        Available qty is ignored in this method

        :param agreement: an agreement browse record

        :returns: a string - "running" if now is between,
                           - "future" if agreement is in future,
                           - "closed" if agreement is outdated

        """
        now = datetime.strptime(fields.datetime.now(),
                                DEFAULT_SERVER_DATETIME_FORMAT)
        start = datetime.strptime(agreement.start_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT)
        end = datetime.strptime(agreement.end_date,
                                DEFAULT_SERVER_DATETIME_FORMAT)
        if start > now:
            return 'future'
        elif end < now:
            return 'closed'
        elif start <= now <= end:
            return 'running'
        else:
            raise ValueError('Agreement start/end dates are incorrect')

    def _get_self(self, cr, uid, ids, context=None):
        """ Store field function to get current ids

        :returns: list of current ids

        """
        return ids

    def _compute_state(self, cr, uid, ids, field_name, arg, context=None):
        """ Compute current state of agreement based on date and consumption

        Please refer to function field documentation for more details.

        """
        res = {}
        for agreement in self.browse(cr, uid, ids, context=context):
            dates_state = self._check_running_date(cr, agreement, context=context)
            if dates_state == 'running':
                if agreement.available_quantity <= 0:
                    res[agreement.id] = 'consumed'
                else:
                    res[agreement.id] = 'running'
            else:
                res[agreement.id] = dates_state
        return res

    def _search_state(self, cr, uid, obj, name, args, context=None):
        """Implement search on state function field.

        Only support "and" mode.
        supported opperators are =, in, not in, <>.
        For more information please refer to fnct_search OpenERP documentation.

        """
        if not args:
            return []
        ids = self.search(cr, uid, [], context=context)
        # this can be problematic in term of performace but the
        # state field can be changed by values and time evolution
        # In a business point of view there should be around 30 yearly LTA

        found_ids = []
        res = self.read(cr, uid, ids, ['state'], context=context)
        for field, operator, value in args:
            assert field == name
            if operator == '=':
                found_ids += [frm['id'] for frm in res if frm['state'] in value]
            elif operator == 'in' and isinstance(value, list):
                found_ids += [frm['id'] for frm in res if frm['state'] in value]
            elif operator in ("!=", "<>"):
                found_ids += [frm['id'] for frm in res if frm['state'] != value]
            elif operator == 'not in'and isinstance(value, list):
                found_ids += [frm['id'] for frm in res if frm['state'] not in value]
            else:
                raise NotImplementedError('Search operator %s not implemented for value %s'
                                          % (operator, value))
        to_return = set(found_ids)
        return [('id', 'in', [x['id'] for x in to_return])]

    def _compute_available_qty(self, cr, uid, ids, field_name, arg, context=None):
        """Compute available qty of current agreements.

        Consumption is based on confirmed po lines.
        Please refer to function field documentation for more details.

        """
        company_id = self._company_get(cr, uid, context=None)
        res = {}
        for agreement in self.browse(cr, uid, ids, context=context):
            sql = """SELECT SUM(po_line.product_qty) FROM purchase_order_line AS po_line
            LEFT JOIN purchase_order AS po ON po_line.order_id = po.id
            WHERE date_order BETWEEN DATE(%s) and DATE(%s)
            AND po.partner_id = %s
            AND po.state IN %s
            AND po.company_id = %s"""
            cr.execute(sql, (agreement.start_date, agreement.end_date,
                             agreement.supplier_id.id, AGR_PO_STATE,
                             company_id))
            amount = cr.fetchone()[0]
            if amount is None:
                amount = 0
            res[agreement.id] = agreement.quantity - amount
        return res

    def _get_available_qty(self, cr, uid, ids, field_name, arg, context=None):
        """Compute available qty of current agreements.

        Consumption is based on confirmed po lines.
        Please refer to function field documentation for more details.

        """
        return self._compute_available_qty(cr, uid, ids, field_name, arg, context=context)

    def _get_state(self, cr, uid, ids, field_name, arg, context=None):
        """ Compute current state of agreement based on date and consumption

        Please refer to function field documentation for more details.

        """
        return self._compute_state(cr, uid, ids, field_name, arg, context=context)

    _columns = {'name': fields.char('Number',
                                    required=True,
                                    readonly=True),
                'supplier_id': fields.many2one('res.partner',
                                               'Supplier',
                                               required=True),
                'product_id': fields.many2one('product.product',
                                              'Product',
                                              required=True),
                'start_date': fields.datetime('Begin of Agreement',
                                              required=True),
                'end_date': fields.datetime('End of Agreement',
                                            required=True),
                'delay': fields.integer('Lead time in days'),
                'quantity': fields.integer('Negociated quantity',
                                           required=True),
                'framework_agreement_pricelist_ids': fields.one2many('framework.agreement.pricelist',
                                                                     'framework_agreement_id',
                                                                     'Price lists',
                                                                     required=True),
                'available_quantity': fields.function(_get_available_qty,
                                                      type='integer',
                                                      string='Available quantity',
                                                      readonly=True),
                'state': fields.function(_get_state,
                                         fnct_search=_search_state,
                                         string='state',
                                         type='selection',
                                         selection=[('future', 'Future'),
                                                    ('running', 'Running'),
                                                    ('consumed', 'Consumed'),
                                                    ('closed', 'Closed')],
                                         readonly=True),
                'company_id': fields.many2one('res.company',
                                              'Company')
                }

    def _sequence_get(self, cr, uid, context=None):
        return self.pool['ir.sequence'].get(cr, uid, 'framework.agreement')

    def _company_get(self, cr, uid, context=None):
        return self.pool['res.company']._company_default_get(cr, uid,
                                                             'framework.agreement',
                                                             context=context)

    def _check_overlap(self, cr, uid, ids, context=None):
        """Constraint to check that no agreements for same product/supplier overlap.

        One agreement per product limit is checked if one_agreement_per_product
        is set to True on company

        """
        comp_obj = self.pool['res.company']
        company_id = self._company_get(cr, uid, context=context)
        strict = comp_obj.read(cr, uid, company_id,
                               ['one_agreement_per_product'],
                               context=context)['one_agreement_per_product']
        for agreement in self.browse(cr, uid, ids, context=context):
            # we do not add current id in domain for readability reasons
            overlap = self.search(cr, uid,
                                  ['&',
                                      ('product_id', '=', agreement.product_id.id),
                                      '|',
                                         '&',
                                            ('start_date', '>=', agreement.start_date),
                                            ('start_date', '<=', agreement.end_date),
                                         '&',
                                            ('end_date', '>=', agreement.start_date),
                                            ('end_date', '<=', agreement.end_date),
                                   ])
            # we also look for the one that includes current offer
            overlap += self.search(cr, uid, [('start_date', '<=', agreement.start_date),
                                             ('end_date', '>=', agreement.end_date),
                                             ('id', '!=', agreement.id),
                                             ('product_id', '=', agreement.product_id.id)])
            overlap = self.browse(cr, uid,
                                  [x for x in overlap if x != agreement.id],
                                  context=context)
            # we ensure that there is only one agreement at time per product
            # if strict agreement is set on company
            if strict and overlap:
                return False
            # We ensure that there are not multiple agreements for same supplier at same time
            if any((x.supplier_id.id == agreement.supplier_id.id) for x in overlap):
                return False
        return True

    def check_overlap(self, cr, uid, ids, context=None):
        """Constraint to check that no agreements for same product/supplier overlap.

        One agreement per product limit is checked if one_agreement_per_product
        is set to True on company

        """
        return self._check_overlap(cr, uid, ids, context=context)

    _defaults = {'name': _sequence_get,
                 'company_id': _company_get}

    _sql_constraints = [('date_priority',
                         'check(start_date < end_date)',
                         'Start/end date inversion')]

    _constraints = [(check_overlap,
                     "You can not have overlapping dates for same supplier and product",
                     ('start_date', 'end_date'))]

    def get_all_product_agreements(self, cr, uid, product_id, lookup_dt, qty=None, context=None):
        """Get the all the active agreement of a given product at a given date

        :param product_id: product id of the product
        :param lookup_dt: datetime string of the lookup date
        :param qty: quantity that should be available if parameter is
                    passed and qty is insuffisant no agreement would be returned

        :returns: a list of corresponding agreements or None

        """
        search_args = [('product_id', '=', product_id),
                       ('start_date', '<=', lookup_dt),
                       ('end_date', '>=', lookup_dt)]
        if qty:
            search_args.append(('available_quantity', '>=', qty))
        agreement_ids = self.search(cr, uid, search_args)
        if agreement_ids:
            return self.browse(cr, uid, agreement_ids, context=context)
        return None

    def get_cheapest_agreement_for_qty(self, cr, uid, product_id, date, qty, currency=None, context=None):
        """Return the cheapest agreement that has enough available qty.

        If not enough quantity fallback on the cheapest agreement available
        for quantity.

        :param product_id:
        :param date:
        :param qty:
        :param currency: currency record to make price convertion

        returns (cheapest agreement, enough qty)

        """
        Cheapest = namedtuple('Cheapest', ['cheapest_agreement', 'enough'])
        agreements = self.get_all_product_agreements(cr, uid, product_id,
                                                     date, qty, context=context)
        if not agreements:
            return (None, None)
        agreements.sort(key=lambda x: x.get_price(qty, currency=currency))
        enough = True
        cheapest_agreement = None
        for agr in agreements:
            if agr.available_quantity >= qty:
                cheapest_agreement = agr
                break
        if not cheapest_agreement:
            cheapest_agreement = agreements[0]
            enough = False
        return Cheapest(cheapest_agreement, enough)

    def get_product_agreement(self, cr, uid, product_id, supplier_id,
                              lookup_dt, qty=None, context=None):
        """Get the matching agreement for a given product/supplier at a given date

        :param product_id: product id of the product
        :param supplier_id: supplier to look for agreement
        :param lookup_dt: datetime string of the lookup date
        :param qty: quantity that should be available if parameter is
        passed and qty is insuffisant no aggrement would be returned

        :returns: a corresponding agreement or None

        """
        search_args = [('product_id', '=', product_id),
                       ('supplier_id', '=', supplier_id),
                       ('start_date', '<=', lookup_dt),
                       ('end_date', '>=', lookup_dt)]
        if qty:
            search_args.append(('available_quantity', '>=', qty))
        agreement_ids = self.search(cr, uid, search_args)
        if len(agreement_ids) > 1:
            raise except_orm(_('Many agreements found for the product with id %s'
                               ' at date %s') % (product_id, lookup_dt),
                             _('Please contact your ERP administrator'))
        if agreement_ids:
            agreement = self.browse(cr, uid, agreement_ids[0], context=context)
            return agreement
        return None

    def _get_pricelist_lines(self, cr, uid, agreement,
                             currency, context=None):
        plists = agreement.framework_agreement_pricelist_ids
        plist = next((x for x in plists if x.currency_id == currency), None)
        if not plist:
            raise orm.except_orm(_('Missing Agreement price list'),
                                 _('Please set a price list in currency %s for agreement %s') %
                                 (currency.name, agreement.name))
        return plist.framework_agreement_line_ids

    def get_price(self, cr, uid, agreement_id, qty=0,
                  currency=None, context=None):
        """Return price negociated for quantity

        :returns: price float

        """
        if isinstance(agreement_id, list):
            assert len(agreement_id) == 1
            agreement_id = agreement_id[0]
        current = self.browse(cr, uid, agreement_id, context=context)
        lines = self._get_pricelist_lines(cr, uid, current, currency,
                                          context=context)
        lines.sort(key=attrgetter('quantity'), reverse=True)
        for line in lines:
            if qty >= line.quantity:
                return line.price
        return lines[-1].price

    def _get_currency(self, cr, uid, supplier_id, pricelist_id, context=None):
        """Helper to retrieve correct currency.

        It will look for currency on supplied pricelist if avaiable
        else it will look for partner pricelist currency

        :param supplier_id: supplier of agreement
        :param pricelist_id: primary price list

        :returns: currency browse record

        """

        plist_obj = self.pool['product.pricelist']
        partner_obj = self.pool['res.partner']
        if pricelist_id:
            plist = plist_obj.browse(cr, uid, pricelist_id, context=context)
            return plist.currency_id
        partner = partner_obj.browse(cr, uid, supplier_id, context=context)
        if not partner.property_product_pricelist_purchase:
            raise orm.except_orm(_('No pricelist found'),
                                 _('Please set a pricelist on PO or supplier %s') % partner.name)
        return partner.property_product_pricelist_purchase.currency_id


class Framework_Agreement_pricelist(orm.Model):
    """Price list container"""

    _name = "framework.agreement.pricelist"
    _rec_name = 'currency_id'
    _columns = {'framework_agreement_id': fields.many2one('framework.agreement',
                                                          'Agreement',
                                                          required=True),
                'currency_id': fields.many2one('res.currency',
                                               'Currency',
                                               required=True),
                'framework_agreement_line_ids': fields.one2many('framework.agreement.line',
                                                                'framework_agreement_pricelist_id',
                                                                'Price lines',
                                                                required=True)}


class framework_agreement_line(orm.Model):
    """Price list line of framework agreement
    that contains price and qty"""

    _name = 'framework.agreement.line'
    _description = 'Framework agreement line'
    _rec_name = "quantity"
    _order = "quantity"

    _columns = {'framework_agreement_pricelist_id': fields.many2one('framework.agreement.pricelist',
                                                                    'Price list',
                                                                    required=True),
                'quantity': fields.integer('Quantity',
                                           required=True),

                'price': fields.float('Price', 'Negociated price',
                                      required=True,
                                      digits_compute=dp.get_precision('Product Price'))}


class FrameworkAgreementObservable(object):
    """Base functions for model that have to be (pseudo) observable
    by framework agreement using OpenERP on_change mechanism"""

    def _currency_get(self, cr, uid, pricelist_id, context=None):
        return self.pool['product.pricelist'].browse(cr, uid,
                                                     pricelist_id,
                                                     context=context).currency_id

    def onchange_price_obs(self, cr, uid, ids, price, agreement_id,
                           currency=None, qty=0, context=None):
        """Raise a warning if a agreed price is changed on observed object"""
        if context is None:
            context = {}
        if not agreement_id or context.get('no_chained'):
            return {}
        agr_obj = self.pool['framework.agreement']
        agreement = agr_obj.browse(cr, uid, agreement_id, context=context)
        if agreement.get_price(qty, currency=currency) != price:
            msg = _("You have set the price to %s \n"
                    " but there is a running agreement"
                    " with price %s") % (price, agreement.get_price(qty, currency=currency))
            return {'warning': {'title': _('Agreement Warning!'),
                                'message': msg}}
        return {}

    def onchange_quantity_obs(self, cr, uid, ids, qty, date,
                              product_id, currency=None,
                              supplier_id=None,
                              price_field='price', context=None):
        """Raise a warning if agreed qty is not sufficient when changed on observed object

        :param qty: requested quantity
        :param currency: currency to get price
        :param price field: key on wich we should return price

        :returns: on change dict

        """
        res = {'value': {'framework_agreement_id': False}}
        agreement, status = self._get_agreement_and_qty_status(cr, uid, ids, qty, date,
                                                               product_id,
                                                               supplier_id=supplier_id,
                                                               currency=currency,
                                                               context=context)
        if agreement:
            res['value'] = {price_field: agreement.get_price(qty, currency=currency),
                            'framework_agreement_id': agreement.id}
        if status:
            res['warning'] = {'title': _('Agreement Warning!'),
                              'message': status}
        return res

    def _get_agreement_and_qty_status(self, cr, uid, ids, qty, date,
                                      product_id, supplier_id,
                                      currency=None, context=None):
        """Lookup for agreement and return (matching_agreement, status)

        Agreement or status can be None.

        :param qty: requested quantity
        :param date: date to look for agreement
        :param supplier_id: supplier id who has signed an agreement
        :param product_id: product id to look for an agreement
        :param price field: key on wich we should return price

        :returns: (agreement record, status)

        """
        FoundAgreement = namedtuple('FoundAgreement', ['Agreement', 'message'])
        agreement_obj = self.pool['framework.agreement']
        if supplier_id:
            agreement = agreement_obj.get_product_agreement(cr, uid, product_id,
                                                            supplier_id, date,
                                                            context=context)
        else:
            agreement, enough = agreement_obj.get_cheapest_agreement_for_qty(cr,
                                                                             uid,
                                                                             product_id,
                                                                             date,
                                                                             qty,
                                                                             currency=currency,
                                                                             context=context)
        if agreement is None:
            return (None, None)
        msg = None
        if agreement.available_quantity < qty:
            msg = _("You have ask for a quantity of %s \n"
                    " but there is only %s available"
                    " for current agreement") % (qty, agreement.available_quantity)
        return FoundAgreement(agreement, msg)

    def onchange_product_id_obs(self, cr, uid, ids, qty, date,
                                supplier_id, product_id, pricelist_id=None,
                                currency=None, price_field='price', context=None):
        """
        Lookup for agreement corresponding to product or return None.

        It will raise a warning if not enough available qty.

        :param qty: requested quantity
        :param date: date to look for agreement
        :param supplier_id: supplier id who has signed an agreement
        :param pricelist_id: if of prefered pricelist
        :param product_id: product id to look for an agreement
        :param price field: key on wich we should return price

        :returns: on change dict

        """
        if context is None:
            context = {}
        res = {'value': {'framework_agreement_id': False}}
        if not supplier_id or product_id:
            return res
        agreement, status = self._get_agreement_and_qty_status(cr, uid, ids, qty, date,
                                                               product_id,
                                                               supplier_id=supplier_id,
                                                               currency=currency,
                                                               context=context)
        # agr_obj = self.pool['framework.agreement']
        # currency = agr_obj._get_currency(cr, uid, supplier_id,
        #                                  pricelist_id, context=context)
        if agreement:
            res['value'] = {price_field: agreement.get_price(qty, currency=currency),
                            'framework_agreement_id': agreement.id}
        if status:
            res['warning'] = {'title': _('Agreement Warning!'),
                              'message': status}
        if not agreement:
            context['no_chained'] = True
        print product_id, context
        return res

    def onchange_agreement_obs(self, cr, uid, ids, agreement_id, qty, date, product_id,
                               supplier_id=None, currency=None, price_field='price',
                               context=None):
        res = {}
        if not agreement_id or product_id:
            return res
        agr_obj = self.pool['framework.agreement']
        agreement = agr_obj.browse(cr, uid, agreement_id, context=context)
        if agreement.product_id.id != product_id:
            raise orm.except_orm(_('User Error'),
                                 _('Wrong product for choosen agreement'))
        if supplier_id and agreement.supplier_id.id != supplier_id:
            raise orm.except_orm(_('User Error'),
                                 _('Wrong supplier for choosen agreement'))
        res['value'] = {price_field: agreement.get_price(qty, currency=currency)}
        if agreement.available_quantity < qty:
            msg = _("You have ask for a quantity of %s \n"
                    " but there is only %s available"
                    " for current agreement") % (qty, agreement.available_quantity)
            res['warning'] = {'title': _('Agreement Warning!'),
                              'message': msg}
        return res
