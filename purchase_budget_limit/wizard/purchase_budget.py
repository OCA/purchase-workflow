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

import openerp.netsvc as netsvc
from openerp.osv import fields, osv


class PurchaseBudget(osv.TransientModel):
    _name = 'purchase.budget.wizard'
    _columns = {
        'budget_line_ids': fields.many2many("crossovered.budget.lines",
                                            rel='purchase_budget_lines_rel',
                                            id1='order_id', id2='line_id',
                                            string='Budget Lines',
                                            readonly=True),
    }

    def _get_budget_line_ids(self, cr, uid, context=None):
        """Load the exhausted budget lines related to the Purchase Orders"""
        if context is None:
            context = {}
        if context.get('active_model') != 'purchase.order':
            return []
        return self.pool['purchase.order'].exhausted_budget_lines(
            cr, uid, context.get('active_ids'), context=context)

    def override_budget(self, cr, uid, ids, context=None):
        """Override the Budgets and confirm the Purchase Order"""
        if context is None:
            context = {}
        if context.get('active_model') != 'purchase.order':
            return False

        # Send the workflow signal on every purchase order
        wf_service = netsvc.LocalService("workflow")
        for po_id in context.get('active_ids'):
            wf_service.trg_validate(
                uid, 'purchase.order', po_id, 'purchase_confirm_overbudget',
                cr)
        return {'type': 'ir.actions.act_window_close'}

    _defaults = {
        'budget_line_ids': _get_budget_line_ids
    }
