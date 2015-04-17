# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013-2014 Camptocamp SA
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
##############################################################################
from openerp import models, fields, api, exceptions, osv
from openerp.tools.translate import _


class PurchaseOrderClassic(osv.orm.Model):
    _inherit = "purchase.order"

    STATE_SELECTION = [
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('draftbid', 'Draft Bid'),  # added
        ('bid', 'Bid Encoded'),  # Bid Received renamed into Bid Encoded
        ('bid_selected', 'Bid selected'),  # added
        ('draftpo', 'Draft PO'),  # added
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Canceled')
    ]

    _columns = {
        'state': osv.fields.selection(
            STATE_SELECTION,
            'Status',
            readonly=True,
            help="The status of the purchase order or the quotation request. "
            "A quotation is a purchase order in a 'Draft' status. Then the "
            "order has to be confirmed by the user, the status switch to "
            "'Confirmed'. Then the supplier must confirm the order to change "
            "the status to 'Approved'. When the purchase order is paid and "
            "received, the status becomes 'Done'. If a cancel action occurs "
            "in the invoice or in the reception of goods, the status becomes "
            "in exception.",
            select=True,
            copy=False),
        # Adds track_visibility
        'bid_validity': osv.fields.date(
            'Bid Valid Until',
            track_visibility='always',
            help="Date on which the bid expired"),
    }

    def _default_state(self, cr, uid, context=None):
        if not context:
            return 'draft'
        elif context.get('draft_po'):
            return 'draftpo'
        elif context.get('draft_bid'):
            return 'draftbid'
        else:
            return 'draft'

    _defaults = {
        'state': _default_state,
    }


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _default_type(self):
        if self._context.get('draft_po'):
            return 'purchase'
        elif self._context.get('draft_bid'):
            return 'bid'
        else:
            return 'rfq'

    TYPE_SELECTION = [
        ('rfq', 'Request for Quotation'),
        ('bid', 'Bid'),
        ('purchase', 'Purchase Order')
    ]

    STATES = {
        'draft': [('readonly', False)],
        'sent': [('readonly', False)],
        'draftbid': [('readonly', False)],
        'bid': [('readonly', False)],
        'draftpo': [('readonly', False)],
    }

    type = fields.Selection(
        TYPE_SELECTION,
        'Type',
        required=True,
        readonly=True,
        default=_default_type)
    incoterm_address = fields.Char(
        'Incoterms Place',
        help="Incoterms Place of Delivery. "
             "International Commercial Terms are a series of "
             "predefined commercial terms used in "
             "international transactions.")
    cancel_reason_id = fields.Many2one(
        'purchase.cancel_reason', 'Reason for Cancellation', readonly=True)

    # in pricelist_id and currency_id we change readonly and states to make
    # them identical and avoid problems where the onchange from pricelist to
    # currency is reverted in save. However, the user can still set a currency
    # different from the currency of the pricelist, which is undesirable. See:
    # https://github.com/odoo/odoo/issues/4598
    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        readonly=True,
        required=True,
        states=STATES,
        help="The pricelist sets the currency used for this purchase order. "
             "It also computes the supplier price for the selected "
             "products/quantities.")
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        readonly=True,
        required=True,
        states=STATES)

    @api.model
    def create(self, values):
        # Document can be created as Draft RFQ or Draft PO. We need to log the
        # right message.
        description = self._description
        if self._context.get('draft_bid'):
            self._description = 'Draft Bid'
        elif not self._context.get('draft_po'):
            self._description = 'Request for Quotation'
        order = super(PurchaseOrder, self).create(values)
        self._description = description
        if self._context.get('draft_bid'):
            order.signal_workflow('draft_bid')
        if self._context.get('draft_po'):
            order.signal_workflow('draft_po')
        return order

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if default.get('type') == 'purchase':
            self = self.with_context(draft_po=True)

        newpo = super(PurchaseOrder, self).copy(default=default)

        if newpo.type == 'rfq':
            for line in newpo.order_line:
                line.price_unit = 0.0

        return newpo

    @api.multi
    def wkf_draft_po(self):
        self.message_post(body=_("Converted to draft Purchase Order"),
                          subtype="mail.mt_comment")
        return self.write({'state': 'draftpo', 'type': 'purchase'})

    @api.multi
    def action_cancel(self):
        """ Ask a cancel reason
        """
        model_obj = self.env['ir.model.data']
        view_id = (model_obj
                   .sudo()
                   .get_object_reference('purchase_rfq_bid_workflow',
                                         'action_modal_cancel_reason'))[1]
        ctx = self._context.copy()
        ctx['action'] = 'action_cancel_ok'
        ctx['active_model'] = 'purchase.order'
        ctx['active_ids'] = self.ids
        # TODO: filter based on po type
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal.cancel_reason',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_cancel_ok(self):
        act_modal_cancel_obj = self.env['purchase.action_modal.cancel_reason']
        assert self._context.get('active_id')
        action_modal = act_modal_cancel_obj.browse(self._context['active_id'])
        self.cancel_reason_id = action_modal.reason_id
        # resume the normal course of events for purchase cancel
        return super(PurchaseOrder, self).action_cancel()

    @api.multi
    def wkf_action_cancel(self):
        for element in self:
            if element.state in ('draft', 'sent'):
                message = _("Request for Quotation")
            elif element.state == 'bid':
                message = _("Bid")
            else:
                message = self._description
            message += " " + _("canceled")
            element.message_post(body=message, subtype="mail.mt_comment")
        return super(PurchaseOrder, self).wkf_action_cancel()

    @api.multi
    def bid_received(self):
        ctx = self._context.copy()
        ctx.update({
            'action': 'bid_received_ok',
            'default_datetime': (self.bid_date or
                                 fields.Date.context_today(self)),
        })
        view = self.env.ref('purchase_rfq_bid_workflow.action_modal_bid_date')

        # those will be set by the web layer unless they are already defined
        for e in ('active_model', 'active_ids', 'active_id'):
            if e in ctx:
                del ctx[e]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.action_modal.datetime',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def bid_received_ok(self):
        # TODO: send warning if not all lines have a price
        Wizard = self.env['purchase.action_modal.datetime']
        assert self._context.get('active_id')
        wizard = Wizard.browse(self._context['active_id'])

        self.bid_date = wizard.datetime

        self.message_post(body=_("Bid received and encoded"),
                          subtype="mail.mt_comment")
        self.signal_workflow('bid_received')
        return {}

    @api.multi
    def wkf_bid_received(self):
        # XXX do we need bid_date ?
        return self.write({'state': 'bid', 'type': 'bid'})

    @api.multi
    def _has_lines(self):
        """ Check if all request for quotation have at least a line """
        for rfq in self:
            if not rfq.order_line:
                return False
        return True

    @api.multi
    def wkf_send_rfq(self):
        if not self._has_lines():
            raise exceptions.except_orm(
                _('Error!'),
                _('You cannot send a Request for Quotation without any product'
                  ' line.'))
        return super(PurchaseOrder, self).wkf_send_rfq()

    @api.multi
    def print_quotation(self):
        if not self._has_lines():
            raise exceptions.except_orm(
                _('Error!'),
                _('You cannot print a Request for Quotation without any '
                  'product line.'))
        self.message_post(body=_("Request for Quotation printed"),
                          subtype="mail.mt_comment")
        return super(PurchaseOrder, self).print_quotation()

    @api.multi
    def po_tender_requisition_selected(self):
        """Workflow function that write state 'bid selected'"""
        return self.write({'state': 'bid_selected'})


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draftpo',
                            context=None):

        order_type = context.get('order_type') or 'rfq'

        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order, fiscal_position_id, date_planned, name, price_unit,
            context=context)

        if state == 'draft' and order_type == 'rfq':
            res['value'].update({'price_unit': 0.0})

        elif state in ('sent', 'draftbid', 'bid'):
            if 'price_unit' in res['value']:
                del res['value']['price_unit']

        return res
