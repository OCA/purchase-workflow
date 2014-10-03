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

from openerp import models, fields, api, osv
from openerp.exceptions import except_orm
import openerp.osv.expression as expression
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.float_utils import float_compare


class PurchaseRequisitionClassic(osv.orm.Model):
    _inherit = "purchase.requisition"

    _columns = {
        'req_validity': osv.fields.date(
            "Requested Bid's End of Validity",
            help="Requested validity period requested to the bidder, i.e. "
            "please send bids that stay valid until that date.\n The "
            "bidder is allowed to send a bid with another validity end "
            "date that gets encoded in the bid."),
        'state': osv.fields.selection(
            [('draft', 'Draft'),
             ('in_progress', 'Confirmed'),
             ('open', 'Bids Selection'),
             ('closed', 'Bids Selected'),  # added
             ('done', 'PO Created'),
             ('cancel', 'Canceled')],
            'Status',
            track_visibility='onchange',
            required=True)
    }


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    _description = "Call for Bids"

    # modified fields
    purchase_ids = fields.One2many(
        'purchase.order', 'requisition_id',
        'Purchase Orders',
        states={'done': [('readonly', True)]},
        domain=[('type', 'in', ('rfq', 'bid'))])

    # new fields
    bid_tendering_mode = fields.Selection(
        [('open', 'Open'),
         ('restricted', 'Restricted')],
        'Call for Bids Mode',
        help="- Restricted : you select yourself the bidders and generate a "
             "RFQ for each of those. \n- Open : anybody can bid (you have to "
             "advertise the call for bids) and you directly encode the bids "
             "you received. You are still able to generate RFQ if you want to "
             "contact usual bidders.")
    bid_receipt_mode = fields.Selection(
        [('open', 'Open'),
         ('sealed', 'Sealed')],
        'Bid Receipt Mode',
        required=True,
        help="- Open : The bids can be opened when received and encoded. \n"
             "- Closed : The bids can be marked as received but they have to "
             "be opened \nall at the same time after an opening ceremony "
             "(probably specific to public sector).",
        default='open')
    consignee_id = fields.Many2one(
        'res.partner',
        'Consignee',
        help="Person responsible of delivery")
    dest_address_id = fields.Many2one(
        'res.partner',
        'Delivery Address')
    req_incoterm_id = fields.Many2one(
        'stock.incoterms',
        'Requested Incoterms',
        help="Default value requested to the supplier. International "
             "Commercial Terms are a series of predefined commercial terms "
             "used in international transactions.")
    req_incoterm_address = fields.Char(
        'Requested Incoterms Place',
        help="Incoterm Place of Delivery. International Commercial Terms are a"
             " series of predefined commercial terms used in international "
             "transactions.")
    req_payment_term_id = fields.Many2one(
        'account.payment.term',
        'Requested Payment Term',
        help="Default value requested to the supplier.")
    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        domain=[('type', '=', 'purchase')],
        help="If set that pricelist will be used to generate the RFQ."
        "Mostely used to ask a requisition in a given currency.")
    date_end = fields.Datetime(
        'Bid Submission Deadline',
        help="All bids received after that date won't be valid (probably "
             "specific to public sector).")

    @api.multi
    def _has_product_lines(self):
        """
        Check there are products lines when confirming Call for Bids.
        Called from workflow transition draft->sent.
        """
        for callforbids in self:
            if not callforbids.line_ids:
                raise except_orm(
                    _('Error!'),
                    _('You have to define some products before confirming the '
                      'call for bids.'))
        return True

    @api.model
    def _prepare_purchase_order(self, requisition, supplier):
        values = super(PurchaseRequisition, self
                       )._prepare_purchase_order(requisition, supplier)
        values.update({
            'dest_address_id': requisition.dest_address_id.id,
            'consignee_id': requisition.consignee_id.id,
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id.id,
            'incoterm_id': requisition.req_incoterm_id.id,
            'incoterm_address': requisition.req_incoterm_address,
        })
        if requisition.pricelist_id:
            values['pricelist_id'] = requisition.pricelist_id.id
        return values

    @api.model
    def _prepare_purchase_order_line(self, requisition, requisition_line,
                                     purchase_id, supplier):
        vals = super(PurchaseRequisition, self
                     )._prepare_purchase_order_line(requisition,
                                                    requisition_line,
                                                    purchase_id,
                                                    supplier)
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

    @api.model
    def check_valid_quotation(self, quotation):
        return False

    @api.multi
    def generate_po(self):
        assert len(self.ids) == 1, "Only 1 ID expected"

        for po_line in self.po_line_ids:
            # set bid selected boolean to true on RFQ containing confirmed
            # lines
            if (po_line.state == 'confirmed' and
                    not po_line.order_id.bid_partial):
                po_line.order_id.bid_partial = True

        return super(PurchaseRequisition, self).generate_po()

    @api.model
    def quotation_selected(self, quotation):
        """Predicate that checks if a quotation has at least one line chosen
        :param quotation: record of 'purchase.order'

        :returns: True if one line has been chosen

        """
        # This topic is subject to changes
        return quotation.bid_partial

    @api.model
    def cancel_quotation(self, tender):
        """
        Called from generate_po. Cancel only draft and sent rfq
        """
        tender.refresh()
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent', 'bid']:
                if self.quotation_selected(quotation):
                    quotation.signal_workflow('select_requisition')
                else:
                    quotation.signal_workflow('purchase_cancel')
                    quotation.message_post(
                        body=_('Canceled by the call for bids associated '
                               'to this request for quotation.'))

        return True

    @api.multi
    def tender_open(self):
        """
        Cancel RFQ that have not been sent. Ensure that there are RFQs."
        """
        cancel_ids = []
        rfq_valid = False
        for callforbids in self:
            for purchase in callforbids.purchase_ids:
                if purchase.state == 'draft':
                    cancel_ids.append(purchase.id)
                elif purchase.state != 'cancel':
                    rfq_valid = True
        if cancel_ids:
            reason_id = self.pool.get('ir.model.data').get_object_reference(
                'purchase_extended', 'purchase_cancelreason_rfq_canceled')[1]
            purchase_order_obj = self.pool.get('purchase.order')
            purchase_order_obj.write(cancel_ids, {'cancel_reason': reason_id})
            purchase_order_obj.action_cancel(cancel_ids)
        if not rfq_valid:
            raise except_orm(
                _('Error'), _('You do not have valid sent RFQs.'))
        return super(PurchaseRequisition, self).tender_open()

    @api.one
    def _get_po_to_cancel(self):
        """Get the list of PO/RFQ that can be canceled on RFQ

        :param callforbids: `purchase.requisition` record

        :returns: List of candidate PO/RFQ record

        """
        orders = []
        for purchase in self.purchase_ids:
            if purchase.state in ('draft', 'sent'):
                orders.append(purchase)
        return orders

    @api.one
    def _check_can_be_canceled(self):
        """Raise an exception if callforbids can not be cancelled
        :param callforbids: `purchase.requisition` record

        :returns: True or raise exception

        """
        for purchase in self.purchase_ids:
            if purchase.state not in ('draft', 'sent'):
                raise except_orm(
                    _('Error'),
                    _('You cannot cancel a call for bids which '
                      'has already received bids.'))
        return True

    @api.model
    def _cancel_po_with_reason(self, po_list, reason_id):
        """Cancel purchase order of a tender, using given reasons
        :param po_list: list of po record to cancel
        :param reason_id: reason id of cancelation

        :returns: cancel po record list

        """
        for order in po_list:
            order.cancel_reason = reason_id
            # passing full list raises assert error
            order.action_cancel_no_reason()
        return po_list

    @api.model
    def _get_default_reason(self):
        """Return default cancel reason"""
        IrModelData = self.env['ir.model.data']
        ref = ('purchase_requisition_extended'
               '.purchase_cancelreason_rfq_canceled')
        reason_id = IrModelData.xmlid_to_res_id(ref)
        return reason_id

    @api.multi
    def tender_cancel(self):
        """
        Cancel call for bids and try to cancelrelated  RFQs/PO

        """
        reason_id = self._get_default_reason()
        for callforbid in self:
            callforbid._check_can_be_canceled()
            po_to_cancel = self._get_po_to_cancel()
            if po_to_cancel:
                self._cancel_po_with_reason(po_to_cancel, reason_id)
        self.state = 'cancel'

    @api.multi
    def tender_close(self):
        self.state = 'closed'

    @api.multi
    def open_rfq(self):
        """
        This opens rfq view to view all generated rfq/bids associated to the
        call for bids
        """
        ActWindow = self.env['ir.actions.act_window']
        res = ActWindow.for_xml_id('purchase', 'purchase_rfq')
        res['domain'] = expression.AND([eval(res.get('domain', [])),
                                       [('requisition_id', 'in', self.ids)]])
        # FIXME: need to disable create - temporarily set as invisible in view
        return res

    @api.multi
    def open_po(self):
        """
        This opens po view to view all generated po associated to the call for
        bids
        """
        ActWindow = self.env['ir.actions.act_window']
        res = ActWindow.for_xml_id('purchase', 'purchase_form_action')
        res['domain'] = expression.AND([eval(res.get('domain', [])),
                                       [('requisition_id', 'in', self.ids)]])
        return res

    @api.multi
    def close_callforbids(self):
        """
        Check all quantities have been sourced
        """
        # this method is called from a special JS event and ids is
        # inferred from 'active_ids', in some cases, the webclient send
        # no ids, so we prevent a crash
        if not self.ids:
            raise except_orm(
                _('Error'),
                _('Impossible to proceed due to an error of the system.\n'
                  'Please reopen the purchase requisition and try again '))
        assert len(self.ids) == 1, "Only 1 ID expected, got %s" % self.ids
        dp_obj = self.env['decimal.precision']
        precision = dp_obj.precision_get('Product Unit of Measure')
        for line in self.line_ids:
            qty = line.product_qty
            for pol in line.purchase_line_ids:
                if pol.state == 'confirmed':
                    qty -= pol.quantity_bid
            if qty == line.product_qty:
                break  # nothing selected
            compare = float_compare(qty, 0, precision_digits=precision)
            if compare != 0:
                break  # too much or too few selected
        else:
            return self.close_callforbids_ok()

        # open a dialog to confirm that we want more / less or no qty
        ctx = self.env.context.copy()

        ctx.update({
            'action': 'close_callforbids_ok',
            'active_model': self._name,
            })
        IrModelData = self.env['ir.model.data']
        ref = 'purchase_requisition_extended.action_modal_close_callforbids'
        view_id = IrModelData.xmlid_to_res_id(ref)

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

    @api.multi
    def open_product_line(self):
        """ Filter to show only lines from bids received. Group by requisition
        line instead of product for unicity
        """
        res = super(PurchaseRequisition, self
                    ).open_product_line()
        ctx = res.setdefault('context', {})
        if 'search_default_groupby_product' in ctx:
            del ctx['search_default_groupby_product']
        if 'search_default_hide_cancelled' in ctx:
            del ctx['search_default_hide_cancelled']
        ctx['search_default_groupby_requisitionline'] = True
        ctx['search_default_showbids'] = True
        return res

    @api.multi
    def close_callforbids_ok(self):
        self.signal_workflow('close_bid')
        return False


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    remark = fields.Text('Remark')
    purchase_line_ids = fields.One2many(
        'purchase.order.line',
        'requisition_line_id',
        'Bids Lines',
        readonly=True)

    @api.multi
    def name_get(self):
        res = []
        for line in self:
            name = ""
            if line.schedule_date:
                name += '%s ' % line.schedule_date
            name += '%s %s' % (line.product_qty, line.product_id)
            res.append((line.id, name))
        return res
