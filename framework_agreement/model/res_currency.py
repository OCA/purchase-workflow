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

class res_currency_rate(orm.Model):
    """Add a relation to framework agreement"""

    _inherit = "res.currency.rate"
    _columns = {"framework_agreement_id": fields.many2one('framework.agreement',
                                                          'Related Agreement')}

    def _current_rate_computation(self, cr, uid, ids, name, arg, raise_on_no_rate, context=None):
        """Override of function in order to retrive agreement rate

        Override is active if key from_agreement_id is set in context

        """

        agreement_id = context.get('from_agreement_id')
        if not agreement_id:
            return super(res_currency_rate, self)._current_rate_computation(cr, uid, ids,
                                                                            name, arg,
                                                                            raise_on_no_rate,
                                                                            context=None)
        agreement = self.pool['framework.agreement'].browse(cr, uid, agreement_id,
                                                            context=context)
        res = {}
        # code should be compatible with 2.6
        currency_rate_map = dict((x.currency_id.id, x.id)
                                 for x in agreement.currency_rate_line_ids)
        for c_id in ids:
            rate_id = currency_rate_map.get(c_id)
            if not rate_id and context.get('agreement_rais_on_no_rate'):
                currency = self.pool['res.currency'].browse(cr, uid, c_id)
                raise orm.except_orm(_('Agreement rate is missing'),
                                     _("You have no entries for currency"
                                       " in agreement %s") % (currency.name, agreement.name))
            else:
                res[c_id] = rate_id
        return res
