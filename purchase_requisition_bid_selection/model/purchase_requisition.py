# -*- coding: utf-8 -*-
#
#
#    Copyright 2013, 2014 Camptocamp SA
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
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
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
             ('selected', 'Bids Selected'),  # added
             ('closed', 'Selection Closed'),  # added
             ('done', 'PO Created'),
             ('cancel', 'Canceled')],
            'Status',
            track_visibility='onchange',
            required=True),
        'purchase_ids': osv.fields.one2many(
            'purchase.order',
            'requisition_id',
            'RFQs and Bids',
            states={'done': [('readonly', True)]},
            domain=[('type', 'in', ('rfq', 'bid'))]),
        'generated_order_ids': osv.fields.one2many(
            'purchase.order',
            'requisition_id',
            'Generated Purchase Orders',
            states={'done': [('readonly', True)]},
            domain=[('type', '=', 'purchase')]),
    }


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    _description = "Call for Bids"

    # new fields
    bid_tendering_mode = fields.Selection(
        [('open', 'Open'),
         ('restricted', 'Restricted')],
        'Call for Bids Mode',
        required=True,
        default='open',
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
    req_terms_of_payment = fields.Char('Requested Terms of Payment')
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
    delivery_remark = fields.Text('Delivery Remarks')
    budget = fields.Float()
    selection_reasons = fields.Text(copy=False)

    # Report fields
    bid_ids = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='requisition_id',
        domain=[('type', '=', 'bid')],
    )
    eligible_bid_ids = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='requisition_id',
        domain=[('type', '=', 'bid'),
                ('state', 'in', ('draftbid', 'bid')),
                ('bid_eligible', '=', True)],
    )

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
            'bid_validity': requisition.req_validity,
            'payment_term_id': requisition.req_payment_term_id.id,
            'incoterm_id': requisition.req_incoterm_id.id,
            'incoterm_address': requisition.req_incoterm_address,
            'delivery_remark': requisition.delivery_remark,
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
        vals.update(
            price_unit=0,
            requisition_line_id=requisition_line.id,
            remark=requisition_line.remark,
        )
        return vals

    @api.model
    def check_valid_quotation(self, quotation):
        return False

    def _prepare_po_from_tender(self, cr, uid, tender, context=None):
        """Give the generated PO the correct type and state
        and propagate the Delivery Remarks from tender"""
        result = super(PurchaseRequisition, self)._prepare_po_from_tender(
            cr, uid, tender, context)
        result.update({
            'type': 'purchase',
            'state': 'draftpo',
            'keep_in_draft': True,
        })
        return result

    @api.multi
    def generate_po(self):
        self.ensure_one()

        for po_line in self.po_line_ids:
            # set bid selected boolean to true on RFQ containing confirmed
            # lines
            if (po_line.state == 'confirmed' and
                    not po_line.order_id.bid_partial):
                po_line.order_id.bid_partial = True

        result = super(PurchaseRequisition, self).generate_po()
        self.generated_order_ids.write({'keep_in_draft': False})
        return result

    @api.model
    def quotation_selected(self, quotation):
        """Predicate that checks if a quotation has at least one line chosen
        :param quotation: record of 'purchase.order'

        :returns: True if one line has been chosen

        """
        # This topic is subject to changes
        return quotation.bid_partial

    @api.model
    def cancel_unconfirmed_quotations(self, tender):
        """
        Called from generate_po. Cancel only draft and sent rfq
        """
        tender.refresh()
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent', 'draftbid', 'bid']:
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
        pos_to_cancel = self.env['purchase.order']
        rfq_valid = False
        for callforbids in self:
            for purchase in callforbids.purchase_ids:
                if purchase.state == 'draft':
                    pos_to_cancel |= purchase
                elif purchase.state != 'cancel':
                    rfq_valid = True
        if pos_to_cancel:
            reason = self.env.ref(
                'purchase_rfq_bid_workflow.'
                'purchase_cancel_reason_rfq_canceled')
            pos_to_cancel.write({'cancel_reason': reason.id})
            pos_to_cancel.action_cancel()
        if not rfq_valid:
            raise except_orm(
                _('Error'), _('You do not have valid sent RFQs.'))
        return super(PurchaseRequisition, self).tender_open()

    @api.multi
    def _get_po_to_cancel(self):
        """Get the list of PO/RFQ that can be cancelled on RFQ

        :returns: List of candidate PO/RFQ record

        """
        purchases = self.mapped('purchase_ids')
        return purchases.filtered(lambda rec: rec.state in ('draft', 'sent'))

    @api.model
    def _cancel_po_with_reason(self, po_list, reason_id):
        """Cancel purchase order of a tender, using given reasons
        :param po_list: list of po record to cancel
        :param reason_id: reason id of cancelation

        :returns: cancel po record list

        """
        po_list.write({'cancel_reason': reason_id})
        po_list.signal_workflow('purchase_cancel')
        return po_list

    @api.model
    def _get_default_reason(self):
        """Return default cancel reason"""
        reason = self.env.ref('purchase_requisition_bid_selection'
                              '.purchase_cancelreason_callforbids_canceled')
        return reason.id

    @api.multi
    def tender_cancel(self):
        """
        Cancel call for bids and try to cancel related RFQs/PO

        """
        self.ensure_one()
        po_to_cancel = self.mapped('purchase_ids')
        if po_to_cancel:
            self._cancel_po_with_reason(po_to_cancel,
                                        self._get_default_reason())
        self.state = 'cancel'

    @api.multi
    def update_selection_reasons(self):
        wizard = self.env['purchase.action_modal.'
                          'ask_selection_reasons'].browse(
            self.env.context['active_id']
        )
        self.selection_reasons = wizard.selection_reasons
        self.signal_workflow('bid_selected')

    @api.multi
    def update_validity(self):
        wizard = self.env['purchase.action_modal.'
                          'ask_validity'].browse(
            self.env.context['active_id']
        )
        self.message_post(body=_('Validity extended from %s to %s')
                          % (self.req_validity, wizard.validity))
        self.req_validity = wizard.validity

    @api.multi
    def tender_selected(self):
        self.state = 'selected'

    @api.multi
    def act_tender_closed(self):
        self.signal_workflow('close_bid')

    @api.multi
    def tender_closed(self):
        self.state = 'closed'

    @api.multi
    def open_rfq(self):
        """
        This opens rfq view to view all generated rfq/bids associated to the
        call for bids
        """
        ActWindow = self.env['ir.actions.act_window']
        res = ActWindow.for_xml_id('purchase', 'purchase_rfq')
        res['domain'] = expression.AND([safe_eval(res.get('domain', [])),
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
        res['domain'] = expression.AND([safe_eval(res.get('domain', [])),
                                       [('requisition_id', 'in', self.ids)]])
        return res

    @api.multi
    def confirm_selection(self):
        """
        Check all quantities have been sourced
        """
        self.ensure_one()
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
            return self.ask_selection_reasons()

        # open a dialog to confirm that we want more / less or no qty
        ctx = self.env.context.copy()

        ctx.update({'action': 'ask_selection_reasons',
                    'active_model': self._name,
                    'active_ids': self.ids,
                    })
        view = self.env.ref('purchase_requisition_bid_selection'
                            '.action_modal_confirm_different_quantity')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def ask_confirmation_to_close_selection(self):
        ctx = self.env.context.copy()

        ctx.update({'action': 'act_tender_closed',
                    'active_model': self._name,
                    'active_ids': self.ids,
                    })
        view = self.env.ref('purchase_requisition_bid_selection'
                            '.modal_confirm_close_selection')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def open_product_line(self, cr, uid, ids, context=None):
        """ Filter to show only lines from bids received.
        Group by requisition line instead of product for unicity.
        """
        res = super(PurchaseRequisition, self).open_product_line(
            cr, uid, ids, context=context)
        ctx = res.setdefault('context', {})
        if 'search_default_groupby_product' in ctx:
            del ctx['search_default_groupby_product']
        if 'search_default_hide_cancelled' in ctx:
            del ctx['search_default_hide_cancelled']
        ctx['search_default_groupby_requisitionline'] = True
        ctx['search_default_showbids'] = True
        ctx['search_default_selection_view'] = True
        return res

    @api.multi
    def ask_validity(self):
        ctx = self.env.context.copy()
        ctx.update({
            'action': 'update_validity',
            'active_model': self._name,
            'active_ids': self.ids,
            'default_validity': self.req_validity,
        })
        view = self.env.ref('purchase_requisition_bid_selection.'
                            'ask_validity')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal.ask_validity',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def ask_selection_reasons(self):
        ctx = self.env.context.copy()
        ctx.update({
            'action': 'update_selection_reasons',
            'active_model': self._name,
            'active_ids': self.ids,
            'default_selection_reasons': self.selection_reasons,
        })
        view = self.env.ref('purchase_requisition_bid_selection.'
                            'ask_selection_reasons')

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal.ask_selection_reasons',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx,
        }


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    remark = fields.Text('Remarks / Conditions')
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
            name += '%s %s' % (line.product_qty, line.product_id.name)
            res.append((line.id, name))
        return res
