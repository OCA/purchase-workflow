# -*- coding: utf-8 -*-

from openerp.osv import fields, orm
import openerp.osv.expression as expression
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.float_utils import float_compare


class PurchaseRequisition(orm.Model):
    _inherit = "purchase.requisition"
    _description = "Call for Bids"
    _columns = {
        # modified
        'state': fields.selection([('draft', 'Draft'),
                                   ('in_progress', 'Confirmed'),
                                   ('open', 'Bids Selection'),
                                   ('closed', 'Bids Selected'),  # added
                                   ('done', 'PO Created'),
                                   ('cancel', 'Canceled')],
                                  'Status', track_visibility='onchange', required=True),
        'purchase_ids': fields.one2many('purchase.order', 'requisition_id', 'Purchase Orders',
                                         states={'done': [('readonly', True)]},
                                         domain=[('type', 'in', ('rfq', 'bid'))]),
        # new
        'req_validity': fields.date("Requested Bid's End of Validity",
                                    help="Default value requested to "
                                         "the supplier."),
        'bid_tendering_mode': fields.selection([('open', 'Open'),
                                                ('restricted', 'Restricted')],
                                               'Call for Bids Mode'),
        'bid_receipt_mode': fields.selection([('open', 'Open'),
                                              ('sealed', 'Sealed')],
                                             'Bid Receipt Mode',
                                             required=True),
        'consignee_id': fields.many2one('res.partner',
                                        'Consignee',
                                        help="Person responsible of delivery"),
        'dest_address_id': fields.many2one('res.partner',
                                           'Delivery Address'),
        'req_incoterm_id': fields.many2one(
            'stock.incoterms',
            'Requested Incoterms',
            help="Default value requested to the supplier. "
                 "International Commercial Terms are a series of predefined "
                 "commercial terms used in international transactions."),
        'req_incoterm_address': fields.char(
            'Requested Incoterms Place',
            help="Incoterm Place of Delivery. "
                 "International Commercial Terms are a series of "
                 "predefined commercial terms used in "
                 "international transactions."),
        'req_payment_term_id': fields.many2one(
            'account.payment.term',
            'Requested Payment Term',
            help="Default value requested to the supplier."),
    }
    _defaults = {
        'bid_receipt_mode': 'open',
    }

    def _has_product_lines(self, cr, uid, ids, context=None):
        """
        Check there are products lines when confirming Call for Bids.
        Called from workflow transition draft->sent.
        """
        for callforbids in self.browse(cr, uid, ids, context=context):
            if not callforbids.line_ids:
                raise orm.except_orm(
                        _('Error!'),
                        _('You have to define some products before confirming the call for bids.'))
        return True

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        values = super(PurchaseRequisition, self)._prepare_purchase_order(
            cr, uid, requisition, supplier, context=context)
        values.update({
            'dest_address_id': requisition.dest_address_id.id,
            'consignee_id': requisition.consignee_id.id,
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id.id,
            'incoterm_id': requisition.req_incoterm_id.id,
            'incoterm_address': requisition.req_incoterm_address,
        })
        return values

    def _prepare_purchase_order_line(self, cr, uid, requisition,
                                     requisition_line, purchase_id,
                                     supplier, context=None):
        vals = super(PurchaseRequisition, self)._prepare_purchase_order_line(
            cr, uid, requisition, requisition_line, purchase_id, supplier, context)
        vals['price_unit'] = 0
        vals['requisition_line_id'] = requisition_line.id
        return vals

    def onchange_dest_address_id(self, cr, uid, ids, dest_address_id,
                                 warehouse_id, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        dest_ids = warehouse_obj.search(cr, uid,
                                        [('partner_id', '=', dest_address_id)],
                                        context=context)
        if dest_ids:
            if warehouse_id not in dest_ids:
                warehouse_id = dest_ids[0]
        else:
            warehouse_id = False
        return {'value': {'warehouse_id': warehouse_id}}

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        if not warehouse_id:
            return {}
        warehouse_obj = self.pool.get('stock.warehouse')
        warehouse = warehouse_obj.browse(cr, uid,
                                         warehouse_id, context=context)
        dest_id = warehouse.partner_id.id
        return {'value': {'dest_address_id': dest_id}}

    def trigger_validate_po(self, cr, uid, po_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', po_id, 'draft_po', cr)
        po_obj = self.pool.get('purchase.order')
        po_obj.write(cr, uid, po_id, {'bid_partial': False}, context=context)
        return True

    def check_valid_quotation(self, cr, uid, quotation, context=None):
        return False

    def generate_po(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID expected"
            ids = ids[0]
        tender = self.browse(cr, uid, ids, context=context)
        po_obj = self.pool.get('purchase.order')
        for po_line in tender.po_line_ids:
            # set bid selected boolean to true on RFQ containing confirmed lines
            if (po_line.state == 'confirmed' and
                    not po_line.order_id.bid_partial):
                po_obj.write(cr, uid,
                             po_line.order_id.id,
                             {'bid_partial': True},
                             context=context)
        return super(PurchaseRequisition, self).generate_po(cr, uid, [ids], context=context)

    def cancel_quotation(self, cr, uid, tender, context=None):
        """
        Called from generate_po. Cancel only draft and sent rfq
        """
        po = self.pool.get('purchase.order')
        wf_service = netsvc.LocalService("workflow")
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent']:
                wf_service.trg_validate(uid, 'purchase.order', quotation.id, 'purchase_cancel', cr)
                po.message_post(cr, uid, [quotation.id],
                        body=_('Canceled by the call for bids associated to this request for quotation.'),
                        context=context)

        return True

    def tender_open(self, cr, uid, ids, context=None):
        """
        Cancel RFQ that have not been sent. Ensure that there are RFQs."
        """
        cancel_ids = []
        rfq_valid = False
        for callforbids in self.browse(cr, uid, ids, context=context):
            for purchase in callforbids.purchase_ids:
                if purchase.state == 'draft':
                    cancel_ids.append(purchase.id)
                elif purchase.state != 'cancel':
                    rfq_valid = True
        if cancel_ids:
            reason_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
                            'purchase_extended', 'purchase_cancelreason_rfq_canceled')[1]
            purchase_order_obj = self.pool.get('purchase.order')
            purchase_order_obj.write(cr, uid, cancel_ids, {'cancel_reason': reason_id}, context=context)
            purchase_order_obj.action_cancel(cr, uid, cancel_ids, context=context)
        if not rfq_valid:
            raise orm.except_orm(
                        _('Error'),
                        _('You do not have valid sent RFQs.'))
        return super(PurchaseRequisition, self).tender_open(cr, uid, ids, context=context)

    def tender_cancel(self, cr, uid, ids, context=None):
        """
        Try to cancel all RFQs
        """
        cancel_ids = []
        for callforbids in self.browse(cr, uid, ids, context=context):
            for purchase in callforbids.purchase_ids:
                if (purchase.state in ('draft', 'sent')):
                    cancel_ids.append(purchase.id)
                else:
                    raise orm.except_orm(
                        _('Error'),
                        _('You cannot cancel a call for bids which has already received bids.'))
        if cancel_ids:
            reason_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
                            'purchase_requisition_extended', 'purchase_cancelreason_callforbids_canceled')[1]
            purchase_order_obj = self.pool.get('purchase.order')
            purchase_order_obj.write(cr, uid, cancel_ids, {'cancel_reason': reason_id}, context=context)
            purchase_order_obj.action_cancel(cr, uid, [purchase.id])
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def tender_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'closed'}, context=context)

    def open_rfq(self, cr, uid, ids, context=None):
        """
        This opens rfq view to view all generated rfq/bids associated to the call for bids
        """
        if context is None:
            context = {}
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'purchase', 'purchase_rfq', context=context)
        res['domain'] = expression.AND([eval(res.get('domain', [])), [('requisition_id', 'in', ids)]])
        # FIXME: need to disable create - temporarily set as invisible in view
        return res

    def open_po(self, cr, uid, ids, context=None):
        """
        This opens po view to view all generated po associated to the call for bids
        """
        if context is None:
            context = {}
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'purchase', 'purchase_form_action', context=context)
        res['domain'] = expression.AND([eval(res.get('domain', [])), [('requisition_id', 'in', ids)]])
        return res

    def open_product_line(self, cr, uid, ids, context=None):
        """ Filter to show only lines from bids received. Group by requisition line instead of product for unicity
        """
        res = super(PurchaseRequisition, self).open_product_line(cr, uid, ids, context=context)
        ctx = res.setdefault('context', {})
        if 'search_default_groupby_product' in ctx:
            del ctx['search_default_groupby_product']
        if 'search_default_hide_cancelled' in ctx:
            del ctx['search_default_hide_cancelled']
        ctx['search_default_groupby_requisitionline'] = True
        ctx['search_default_showbids'] = True
        return res

    def close_callforbids(self, cr, uid, ids, context=None):
        """
        Check all quantities have been sourced
        """
        # this method is called from a special JS event and ids is
        # inferred from 'active_ids', in some cases, the webclient send
        # no ids, so we prevent a crash
        if not ids:
            raise orm.except_orm(
                _('Error'),
                _('Impossible to proceed due to an error of the system.\n'
                  'Please reopen the purchase requisition and try again '))
        if isinstance(ids, (tuple, list)):
            assert len(ids) == 1, "Only 1 ID expected, got %s" % ids
            ids = ids[0]
        purch_req = self.browse(cr, uid, ids, context=context)
        dp_obj = self.pool.get('decimal.precision')
        precision = dp_obj.precision_get(cr, uid, 'Product Unit of Measure')
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
        return self.close_callforbids_ok(cr, uid, [ids], context=context)

    def close_callforbids_ok(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_validate(uid, 'purchase.requisition',
                                    id, 'close_bid', cr)
        return False


class PurchaseRequisitionLine(orm.Model):
    _inherit = "purchase.requisition.line"
    _columns = {
        'remark': fields.text('Remark'),
        'purchase_line_ids': fields.one2many('purchase.order.line', 'requisition_line_id', 'Bids Lines', readonly=True),
    }

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.read(cr, uid, ids, ['product_id', 'product_qty', 'schedule_date'], context=context):
            name = ""
            if line['schedule_date']:
                name += '%s ' % line['schedule_date']
            name += '%s %s' % (line['product_qty'], line['product_id'][1])
            res.append((line['id'], name))
        return res
