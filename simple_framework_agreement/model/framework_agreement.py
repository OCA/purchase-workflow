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
from datetime import datetime
from openerp.osv import orm, fields
from openerp.osv.orm import except_orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class framework_agreement(orm.Model):
    """Long term agreement on product price with a supplier"""

    _name = 'framework.agreement'

    def _check_running_date(self, cr, agreement, context=None):
        """ Validate that the current agreement is actually active
        using date only
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
        elif now >= start and now <= end:
            return 'running'
        else:
            raise ValueError('Agreement start/end dates are incorrect')

    def _get_self(self, cr, uid, ids, context=None):
        """ Store field function to get current ids"""
        return ids

    def _compute_state(self, cr, uid, ids, field_name, arg, context=None):
        """ Compute current state of agreement based on date and consumed
        amount"""
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
        """Implement serach on field in "and" mode only.
        supported opperators are =, in, not in, <>.
        For more information please refer to fnct_search OpenERP documentation"""
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
                raise NotImplementedError('Search operator % not implemented for value %s'
                                          % (operator, value))
        to_return = set(found_ids)
        return [('id', 'in', [x['id'] for x in to_return])]

    def _get_state(self, cr, uid, ids, field_name, arg, context=None):
        """Return current state of agreement"""
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
                'price': fields.float('Price', 'Negociated price',
                                      required=True,
                                      digits_compute=dp.get_precision('Product Price')),
                'available_quantity': fields.integer('Available quantity'), # To be transformer in function field
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

    def check_overlap(self, cr, uid, ids, context=None):
        """ Constraint to check that no agreements for same product
        and supplier overlap"""
        for agreement in self.browse(cr, uid, ids, context=context):
            # we do not add current id in domain for readability reasons
            overlap = self.search(cr, uid, ['&', '&',
                                            ('product_id', '=', agreement.product_id.id),
                                            ('supplier_id', '=', agreement.supplier_id.id),
                                            '|', '&',
                                            ('start_date', '>=', agreement.start_date),
                                            ('start_date', '<=', agreement.end_date),
                                            '&',
                                            ('end_date', '>=', agreement.start_date),
                                            ('end_date', '<=', agreement.end_date)])
            # we also look for the one that include current offer
            overlap += self.search(cr, uid, [('start_date', '<=', agreemment.start_date),
                                             ('end_date', '>=', agreement.end_date),
                                             ('id', '!=', agreement.id),
                                             ('product_id', '=', agreement.product_id.id),
                                             ('supplier_id', '=', agreement.supplier_id.id),])
            overlap = [x for x in overlap if x != agreement.id]
            if overlap:
                return False
        return True

    _defaults = {'name': _sequence_get}

    _sql_constraints = [('date_priority',
                         'check(start_date < end_date)',
                         'Start/end date inversion')]

    _constraints = [(check_overlap,
                     "You can not have overlapping dates for same supplier and product",
                     ('start_date', 'end_date'))]

    def get_product_agreement_price(self, cr, uid, product_id, supplier_id,
                                    lookup_dt, qty=None, context=None):
        """ get the agreement price of a given product at a given date
        :param product_id: product id of the product
        :param supplier_id: supplier to look for agreement
        :param lookup_dt: datetime string of the lookup date
        :param qty: quantity that should be available
        :returns: a corresponding float price or None"""
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
            return agreement.price
        return None
