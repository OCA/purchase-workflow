# -*- coding: utf-8 -*-

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('bid', 'Bid Received'),
        ('draftpo', 'Draft PO'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    _columns = {
        'state': fields.selection(
            STATE_SELECTION,
            'Status',
            readonly=True,
            help="The status of the purchase order or the quotation request. "
                 "A quotation is a purchase order in a 'Draft' status. "
                 "Then the order has to be confirmed by the user, "
                 "the status switch to 'Confirmed'. "
                 "Then the supplier must confirm the order to change the "
                 "status to 'Approved'. When the purchase order is paid and "
                 "received, the status becomes 'Done'. "
                 "If a cancel action occurs in the invoice or in the "
                 "reception of goods, the status becomes in exception.",
                 select=True),
        'bid_encoded': fields.boolean('Bid encoded',
                                      help="True if the bid has been encoded"),
        'bid_partial': fields.boolean(
            'Bid partially selected',
            readonly=True,
            help="True if the bid has been partially selected"),
        'consignee_id': fields.many2one(
            'res.partner',
            'Consignee',
            help="Person responsible of delivery"),
        'tender_bid_receipt_mode': fields.function(
            lambda self, *args, **kwargs: self._get_tender(*args, **kwargs),
            multi="callforbids",
            readonly=True,
            type='selection',
            selection=[('open', 'Open'), ('sealed', 'Sealed')],
            string='Bid Receipt Mode'),
    }
    _defaults = {
        'state': lambda self, cr, uid, context: 'draftpo' if context.get('draft_po') else 'draft',
    }

    def _get_tender(self, cr, uid, ids, fields, args, context=None):
        orders = self.read(cr, uid, ids, ['requisition_id'],
                           context=context, load='_classic_write')
        # TODO rewrite
        requisition_ids = list(set(filter(None, [x['requisition_id'] for x in orders])))
        requisitions = requisition_ids and self.pool.get('purchase.requisition').read(cr, uid, requisition_ids,
                        [x[len('tender_'):] for x in fields],
                        context=context, load='_classic_write')
        requisitions = dict([(x['id'], dict([('tender_' + k,v) for k,v in x.iteritems() if 'tender_' + k in fields])) for x in requisitions])
        res = {}
        for po in orders:
            res[po['id']] = po['requisition_id'] and requisitions[po['requisition_id']] or dict([(x, False) for x in fields])
        return res

    def create(self, cr, uid, vals, context=None):
        newly_id = super(purchase_order, self).create(cr, uid, vals, context=context)
        if context is None:
            context = {}
        if context.get('draft_po'):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'purchase.order',
                                    newly_id, 'draft_po', cr)
        return newly_id

    def encode_bid(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'bid_encoded': True}, context=context)

    def action_cancel_draft(self, cr, uid, ids, context=None):
        super(purchase_order, self).action_cancel_draft(cr, uid, ids,
                                                        context=context)
        return self.write(cr, uid, ids, {'bid_encoded': False}, context=context)

    def wkf_draft_po(self, cr, uid, ids, context=None):
        for element in self.browse(cr, uid, ids, context=context):
            if (not element.bid_encoded and
                    element.state not in ('draft', 'draftpo')):
                raise orm.except_orm(
                    _('Warning'),
                    _('You cannot convert a RFQ to a PO while '
                      'bid has not been encoded.'))
        return self.write(cr, uid, ids, {'state': 'draftpo'}, context=context)

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

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id,
                            qty, uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            context=None):
        res = super(purchase_order_line, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)
        if state in ('draft', 'sent'):
            # need to add an argument which is the state of po,
            # otherwise impossible to know if we need to return price_unit
            # of zero or not
            res['value']['price_unit'] = 0
        return res
