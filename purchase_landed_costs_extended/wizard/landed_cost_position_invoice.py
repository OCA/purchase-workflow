# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
from openerp.osv import osv
from openerp.tools.translate import _


class landed_cost_position_invoice(osv.osv_memory):

    """ To create invoice for purchase order line"""

    _name = 'landed.cost.position.invoice'
    _description = 'Landed Cost Position Make Invoice'

    def make_invoices(self, cr, uid, ids, context=None):

        context = context or None
        record_ids = context.get('active_ids', [])
        invoice_ids = []
        if record_ids:
            lcp_pool = self.pool.get('landed.cost.position')
            po_pool = self.pool.get('purchase.order')

            for order_cost in lcp_pool.browse(cr, uid, record_ids,
                                              context=context):
                if order_cost.generate_invoice and not order_cost.invoice_id:
                    inv_id = po_pool._generate_invoice_from_landed_cost(
                        cr, uid, order_cost, context=context)
                    invoice_ids.append(inv_id)
        domain = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        return {
            'domain': domain,
            'name': _('Landed Cost Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }
