# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class PurchaseRequisition(osv.Model):
    _inherit = "purchase.requisition"
    _columns = {
        'req_validity': fields.date('Requested Bid\'s End of Validity', help="Default value requested to the supplier."),
        'bid_tendering_mode': fields.selection([('open','Open'),('restricted','Restricted')], 'Bid Tendering Mode', required=True),
        'bid_receipt_mode': fields.selection([('open','Open'),('sealed','Sealed')], 'Bid Receipt Mode', required=True),
        'consignee_id': fields.many2one('res.partner', 'Consignee', help="Person responsible of delivery"),
        'dest_address_id':fields.many2one('res.partner', 'Delivery Address',
            #states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]},
        ),
        'req_incoterm_id': fields.many2one('stock.incoterms', 'Requested Incoterm', help="Default value requested to the supplier. International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'req_incoterm_address': fields.char(
            'Requested Incoterm Place',
            help="Incoterm Place of Delivery. "
                 "International Commercial Terms are a series of "
                 "predefined commercial terms used in "
                 "international transactions."),
        'req_payment_term_id': fields.many2one('account.payment.term', 'Requested Payment Term', help="Default value requested to the supplier."),

    }
    _defaults = {
        'bid_receipt_mode': 'open',
        'bid_tendering_mode': 'open',
    }

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        d=super(PurchaseRequisition,self)._prepare_purchase_order(cr, uid, requisition, supplier, context=context)
        d.update({
            'dest_address_id': requisition.dest_address_id.id,
            'consignee_id': requisition.consignee_id.id,
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id.id,
            'incoterm_id': requisition.req_incoterm_id.id,
            'incoterm_address': requisition.req_incoterm_address,
        })
        return d

    def onchange_dest_address_id(self, cr, uid, ids, dest_address_id, warehouse_id, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        dest_ids = warehouse_obj.search(cr, uid, [('partner_id','=',dest_address_id)], context=context)
        if len(dest_ids)>=1:
            warehouse_id_ret = dest_ids[0]
            for wh in dest_ids:
                if wh == warehouse_id:
                    warehouse_id_ret = wh
        else:
            warehouse_id_ret = False
        return {
            'value': {
                'warehouse_id':warehouse_id_ret,
            }
        }

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):   
        if warehouse_id:
            dest = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context).partner_id.id
            return {
                'value': {
                    'dest_address_id': dest,
                }
            }
        return False

    def trigger_validate_po(self, cr, uid, po_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', po_id, 'draft_po', cr)
        self.pool.get('purchase.order').write(cr, uid, po_id, {'bid_partial': False}, context=context)

    def check_valid_quotation(self, cr, uid, quotation, context=None):
        return False

    def generate_po(self, cr, uid, id, context=None):
        tender = self.browse(cr, uid, id, context=context)[0]
        po = self.pool.get('purchase.order')
        for po_line in tender.po_line_ids:
            #set bid selected boolean to true on RFQ containing confirmed lines
            if po_line.state == 'confirmed' and not po_line.order_id.bid_partial:
                po.write(cr, uid, po_line.order_id.id, {'bid_partial': True}, context=context)
        super(PurchaseRequisition,self).generate_po(cr, uid, id, context=context)

    def tender_cancel(self, cr, uid, ids, context=None):
        purchase_order_obj = self.pool.get('purchase.order')
        #try to set all associated quotations to cancel state
        for purchase in self.browse(cr, uid, ids, context=context):
            for purchase_id in purchase.purchase_ids:
                if (purchase_id.state in ('draft', 'sent')):
                    purchase_order_obj.action_cancel(cr,uid,[purchase_id.id])
                    purchase_order_obj.message_post(cr, uid, [purchase_id.id], body=_('This quotation has been cancelled.'), subtype="mail.mt_comment", context=context)
                else:
                    raise osv.except_osv(_('Warning!'), _('You cannot cancel a tender which has already received bids.'))
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def _prepare_purchase_order_line(self, cr, uid, requisition, requisition_line, purchase_id, supplier, context=None):
        vals = super(PurchaseRequisition,self)._prepare_purchase_order_line(cr, uid, requisition, requisition_line, purchase_id, supplier, context)
        vals['price_unit'] = 0
        return vals

class PurchaseRequisitionLine(osv.Model):
    _inherit = "purchase.requisition.line"
    _columns = {
        'remark': fields.text('Remark'),
    }
