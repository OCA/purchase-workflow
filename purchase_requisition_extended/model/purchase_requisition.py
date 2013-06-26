# -*- coding: utf-8 -*-

from openerp.orm import fields, orm
from openerp.tools.translate import _
from openerp import netsvc


class PurchaseRequisition(orm.Model):
    _inherit = "purchase.requisition"
    _columns = {
        'req_validity': fields.date("Requested Bid's End of Validity",
                                    help="Default value requested to "
                                         "the supplier."),
        'bid_tendering_mode': fields.selection([('open', 'Open'),
                                                ('restricted', 'Restricted')],
                                               'Call for Bids Mode',
                                               required=True),
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
            'Requested Incoterm',
            help="Default value requested to the supplier. "
                 "International Commercial Terms are a series of predefined "
                 "commercial terms used in international transactions."),
        'req_incoterm_address': fields.char(
            'Requested Incoterm Place',
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
        'bid_tendering_mode': 'open',
    }

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
        tender = self.browse(cr, uid, ids, context=context)[0]
        po_obj = self.pool.get('purchase.order')
        for po_line in tender.po_line_ids:
            # set bid selected boolean to true on RFQ containing confirmed lines
            if (po_line.state == 'confirmed' and
                    not po_line.order_id.bid_partial):
                po_obj.write(cr, uid,
                             po_line.order_id.id,
                             {'bid_partial': True},
                             context=context)
        return super(PurchaseRequisition, self).generate_po(cr, uid, ids,
                                                           context=context)

    def tender_cancel(self, cr, uid, ids, context=None):
        po_obj = self.pool.get('purchase.order')
        #try to set all associated quotations to cancel state
        for purchase in self.browse(cr, uid, ids, context=context):
            for purchase_id in purchase.purchase_ids:
                if (purchase_id.state in ('draft', 'sent')):
                    po_obj.action_cancel(cr, uid, [purchase_id.id])
                    po_obj.message_post(cr, uid,
                                        [purchase_id.id],
                                        body=_('This quotation has been cancelled.'),
                                        subtype="mail.mt_comment",
                                        context=context)
                else:
                    raise orm.except_orm(
                        _('Warning'),
                        _('You cannot cancel a tender which has '
                          'already received bids.'))
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def _prepare_purchase_order_line(self, cr, uid, requisition,
                                     requisition_line, purchase_id,
                                     supplier, context=None):
        vals = super(PurchaseRequisition, self)._prepare_purchase_order_line(
            cr, uid, requisition, requisition_line, purchase_id, supplier, context)
        vals['price_unit'] = 0
        return vals


class PurchaseRequisitionLine(orm.Model):
    _inherit = "purchase.requisition.line"
    _columns = {
        'remark': fields.text('Remark'),
    }
