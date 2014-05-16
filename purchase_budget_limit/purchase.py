# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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

import time

from openerp import netsvc
from openerp.osv import orm
from openerp.tools.translate import _


class PurchaseOrder (orm.Model):
    """Display a warning when confirming a Purchase if the budget is too low"""
    _inherit = 'purchase.order'

    # Initialization (no context)
    def __init__(self, pool, cr):
        """
        Add a new state value.

        Doing it in __init__ is cleaner than copying and pasting the field
        definition in _columns and should be compatible with future/customized
        versions.
        """
        # TODO: new API in v8 probably let us do it in a simpler way
        super(PurchaseOrder, self).__init__(pool, cr)
        super(PurchaseOrder, self).STATE_SELECTION.append(
            ('over_budget', 'Over Budget'))

    # Model methods (context except when called by the Workflow Engine)
    def exhausted_budget_lines(self, cr, uid, ids, context=None):
        """
        Find the Budget Line which do not have enough funds left to pay the POs

        @return: IDs of the Budget Lines
        """
        if not isinstance(ids, list):
            ids = [ids]

        budget_line_ids = set()
        b_line_obj = self.pool['crossovered.budget.lines']
        today = time.strftime('%Y-%m-%d')
        for po_id in ids:
            for ol in self.browse(cr, uid, po_id, context=context).order_line:
                if ol.account_analytic_id:
                    # should we check sub-accounts too?
                    bl_ids = b_line_obj.search(
                        cr, uid,
                        [('analytic_account_id',
                            '=', ol.account_analytic_id.id),
                         ('date_from', '<=', today),
                         ('date_to', '>=', today)],
                        context=context)
                    budget_line_ids.update(
                        [l.id for l in b_line_obj.browse(
                            cr, uid, bl_ids, context=context)
                         if l.crossovered_budget_id.state == 'validate'
                            and (l.practical_amount - ol.price_subtotal
                                 < l.theoritical_amount)])
        return list(budget_line_ids)

    def button_confirm(self, cr, uid, ids, context=None):
        """Advance the workflow and pop up a message on 'Over Budget' state.

        @return: True if all orders are OK, or an client action dictionary to
                 open a confirmation wizard if any order is over-budget.
        """
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]

        # Send the workflow signal on every purchase order
        wf_service = netsvc.LocalService("workflow")
        for po_id in ids:
            wf_service.trg_validate(
                uid, self._name, po_id, 'purchase_confirm', cr)

        # Return True or an Action dictionary
        orders_ok = all([o.state != 'over_budget'
                         for o in self.browse(cr, uid, ids, context=context)])

        return orders_ok or {
            'name': _('Budget warning'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.budget.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': dict(context,
                            active_model='purchase.order',
                            active_ids=ids,
                            active_id=ids[0])
        }
