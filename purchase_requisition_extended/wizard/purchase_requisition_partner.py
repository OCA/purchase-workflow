# -*- coding: utf-8 -*-
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
