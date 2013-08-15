# -*- coding: utf-8 -*-

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID


class purchase_order(orm.Model):
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


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'requisition_line_id': fields.many2one('purchase.requisition.line', 'Call for Bid Line', readonly=True),
    }

    def close_callforbids(self, cr, uid, active_id, context=None):
        """
        Check all quantities have been sourced
        """
        purch_req_obj = self.pool.get('purchase.requisition')
        purch_req = purch_req_obj.browse(cr, uid, active_id, context=context)
        dp_obj = self.pool.get('decimal.precision')
        precision = dp_obj.precision_get(cr, SUPERUSER_ID,
                                         'Product Unit of Measure')
        too_much = False
        too_few = False
        nothing = False
        for line in purch_req.line_ids:
            qty = line.product_qty
            for pol in line.purchase_line_ids:
                if pol.state == 'confirmed':
                    qty -= pol.quantity_bid
            if qty == line.product_qty:
                nothing = True
                break
            compare = float_compare(qty, 0, precision_digits=precision)
            if compare < 0:
                too_much = True
                break
            elif compare > 0:
                too_few = True
                # do not break, maybe a line has too much qty
                # and should be blocked

        if nothing:
            raise orm.except_orm(
                _('Error'),
                _('Nothing has been selected.'))
        elif too_much:
            raise orm.except_orm(
                _('Error'),
                _('The selected quantity cannot be greater than the '
                  'requested quantity'))
        elif too_few:
            # open a dialog to confirm that we want less qty
            ctx = context.copy()
            ctx['action'] = 'close_callforbids_ok'
            ctx['active_model'] = self._name
            get_ref = self.pool.get('ir.model.data').get_object_reference
            view_id = get_ref(cr, uid, 'purchase_requisition_extended',
                              'action_modal_close_callforbids')[1]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.action_modal',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': ctx,
            }
        return self.close_callforbids_ok(cr, uid, [active_id], context=context)

    def close_callforbids_ok(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_validate(uid, 'purchase.requisition', id, 'close_bid', cr)
        return False

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        """Do not aggregate price and qty. We need to do it this way as there
        is no group_operator that can be set to prevent aggregating float"""
        result = super(purchase_order_line, self).read_group(cr, uid, domain, fields, groupby,
                        offset=offset, limit=limit, context=context, orderby=orderby)
        for res in result:
            if 'price_unit' in res:
                del res['price_unit']
            if 'product_qty' in res:
                del res['product_qty']
        return result
