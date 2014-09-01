# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    _columns = {
        'account_analytic_id': fields.many2one(
            'account.analytic.account',
            string='Analytic Account',
            states={'confirmed': [('readonly', True)],
                    'approved': [('readonly', True)],
                    'done': [('readonly', True)]},
            help="The analytic account that will be set on all the lines. "
                 "If you want to use different accounts, leave this field "
                 "empty and set the accounts individually on the lines.")
    }

    def onchange_default_analytic_id(self, cr, uid, ids, account_analytic_id,
                                     order_line, context=None):
        new_commands = []
        if not order_line:
            return {}
        for command in order_line:
            code = command[0]
            if code in (0, 1):
                values = command[2]
                values['account_analytic_id'] = account_analytic_id
                line = code, command[1], values
            elif code == 4:
                values = {'account_analytic_id': account_analytic_id}
                line = 1, command[1], values
            else:
                line = command
            new_commands.append(line)
        vals = {'order_line': new_commands}
        return {'value': vals}
