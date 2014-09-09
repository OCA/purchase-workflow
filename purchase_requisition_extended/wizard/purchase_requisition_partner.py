# -*- coding: utf-8 -*-
#
#
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
#
from openerp.osv import fields, orm
from openerp.tools.translate import _


class purchase_requisition_partner(orm.TransientModel):
    _inherit = "purchase.requisition.partner"

    def create_order(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_id = context and context.get('active_id', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        po_id = self.pool.get('purchase.requisition').make_purchase_order(cr,
                    uid, [active_id], data.partner_id.id,
                    context=context)[active_id]
        if not context.get('draft_bid', False):
            return {'type': 'ir.actions.act_window_close'}
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid,
                    'purchase', 'purchase_rfq', context=context)
        res.update({'res_id': po_id,
                    'views': [(False, 'form')],
                    })
        return res
