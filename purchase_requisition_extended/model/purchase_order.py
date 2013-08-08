# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.float_utils import float_is_zero
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID


class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    _columns = {
        'bid_partial': fields.boolean(
            'Bid partially selected',
            readonly=True,
            help="True if the bid has been partially selected"),
        'tender_bid_receipt_mode': fields.function(
            lambda self, *args, **kwargs: self._get_tender(*args, **kwargs),
            multi="callforbids",
            readonly=True,
            type='selection',
            selection=[('open', 'Open'), ('sealed', 'Sealed')],
            string='Bid Receipt Mode'),
    }
    #TODO: lines should not be deleted or created if linked to a callforbids

    def _get_tender(self, cr, uid, ids, fields, args, context=None):
        # when _classic_write load is used, the many2one are only the
        # ids instead of the tuples (id, name_get)
        purch_req_obj = self.pool.get('purchase.requisition')
        orders = self.read(cr, uid, ids, ['requisition_id'],
                           context=context, load='_classic_write')
        req_ids = list(set(order['requisition_id'] for order in orders
                           if order['requisition_id']))
        # we'll read the fields without the 'tender_' prefix
        # and copy their value in the fields with the prefix
        read_fields = [x[len('tender_'):] for x in fields]
        requisitions = purch_req_obj.read(cr, uid,
                                          req_ids,
                                          read_fields,
                                          context=context,
                                          load='_classic_write')
        # copy the dict but rename the fields with 'tender_' prefix
        tender_reqs = {}
        for req in requisitions:
            tender_reqs[req['id']] = dict(('tender_' + field, value)
                                          for field, value
                                          in req.iteritems()
                                          if 'tender_' + field in fields)
        res = {}
        for po in orders:
            if po['requisition_id']:
                res[po['id']] = tender_reqs[po['requisition_id']]
            else:
                res[po['id']] = {}.fromkeys(fields, False)
        return res

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        values = super(PurchaseRequisition, self)._prepare_purchase_order(
            cr, uid, requisition, supplier, context=context)
        values.update({
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id,
            'incoterm_id': requisition.req_incoterm_id,
            'incoterm_address': requisition.req_incoterm_address,
            'transport_mode_id': requisition.req_transport_mode_id,
        })
        return values


class purchase_order_line(osv.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'requisition_line_id': fields.many2one('purchase.requisition.line', 'Call for Bid Line', readonly=True),
    }

    def close_callforbids(self, cr, uid, active_id, context=None):
        """
        Check all quantities have been sourced
        """
        purchase_requisition_obj = self.pool.get('purchase.requisition')
        valid = True
        callforbids = purchase_requisition_obj.browse(cr, uid, active_id, context=context)
        for line in callforbids.line_ids:
            qty = line.product_qty
            for pol in line.purchase_line_ids:
                qty -= pol.quantity_bid
            precision = self.pool.get('decimal.precision').precision_get(cr, SUPERUSER_ID, 'Product Unit of Measure')
            if not float_is_zero(qty,precision):
                valid = False
        if valid:
            return self.close_callforbids_ok(cr, uid, [active_id], context=context)
        context['action'] = 'close_callforbids_ok'
        context['active_model'] = self._name
        view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
                    'purchase_requisition_extended', 'action_modal_close_callforbids')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    def close_callforbids_ok(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_validate(uid, 'purchase.requisition', id, 'close_bid', cr)
        return False
