# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _purchase_request_confirm_message_content(self, request,
                                                  request_dict):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _('Order confirmation %s for your Request %s') % (
            self.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now been confirmed in Purchase Order %s:') % (
            request.name, self.name)

        for line in request_dict.values():
            message += _(
                '<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>'
            ) % (line['name'],
                 line['product_qty'],
                 line['product_uom'],
                 line['date_planned'],
                 )
        message += '</ul>'
        return message

    @api.multi
    def _purchase_request_confirm_message(self):
        request_obj = self.env['purchase.request']
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        'name': request_line.name,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.name,
                        'date_planned': date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id])
                request.message_post(body=message, subtype='mail.mt_comment')
        return True

    @api.multi
    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == 'done':
                        raise UserError(
                            _('Purchase Request %s has already '
                              'been completed') % request_line.request_id.name)
        return True

    @api.multi
    def button_confirm(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).button_confirm()
        self._purchase_request_confirm_message()
        return res

    @api.multi
    def button_cancel(self):
        """Filters the Purchase Orders (POs):
        * POs with purchase request(s) related go to
        cancel_po_from_request method.
        * POs with no purchase request related are returned to super.
        """
        po_from_request = self.filtered(
            lambda po: po.mapped('order_line.purchase_request_lines'))
        remaining_po = self - po_from_request
        po_from_request.cancel_po_from_request()
        return super(PurchaseOrder, remaining_po).button_cancel()

    @api.multi
    def cancel_po_from_request(self):
        """Filter PO lines of PO that are related to some purchase request
        (PR).
        * Lines which have no relation to PRs are processed with a copy of
        standard code.
        * Lines with relation to PRs aren't processed. The purpose of this is
        to leave on hands of the purchase requests the task of cancelling
        procurements which originated them."""
        for order in self:
            for pick in order.picking_ids:
                if pick.state == 'done':
                    raise UserError(_(
                        'Unable to cancel purchase order %s as some '
                        'receptions have already been done.') % order.name)
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_(
                        "Unable to cancel this purchase order. You must "
                        "first cancel related vendor bills."))
            for pick in order.picking_ids.filtered(
                    lambda r: r.state != 'cancel'):
                pick.action_cancel()
            # Post a msg in purchase requests:
            request_po_lines = order.order_line.filtered(
                lambda pol: pol.purchase_request_lines)
            for line in request_po_lines:
                message = \
                    line._po_line_purchase_request_cancel_message_content()
                requests = line.purchase_request_lines.mapped('request_id')
                for req in requests:
                    req.message_post(body=message, subtype='mail.mt_comment')
            # Search for lines not created from a Purchase request and end
            # the process
            # TODO: remove PO from procurement ?!
            if not self.env.context.get('cancel_procurement'):
                no_request_po_lines = order.order_line.filtered(
                    lambda pol: not pol.purchase_request_lines)
                procurements = no_request_po_lines.mapped('procurement_ids')
                procurements.filtered(lambda r: r.state not in (
                    'cancel', 'exception') and r.rule_id.propagate).write(
                    {'state': 'cancel'})
                procurements.filtered(lambda r: r.state not in (
                    'cancel', 'exception') and not r.rule_id.propagate).write(
                    {'state': 'exception'})
                moves = procurements.filtered(
                    lambda r: r.rule_id.propagate).mapped('move_dest_id')
                moves.filtered(
                    lambda r: r.state != 'cancel').action_cancel()
        self.write({'state': 'cancel'})


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_order_line_id',
        'purchase_request_line_id',
        'Purchase Request Lines', readonly=True, copy=False)

    @api.multi
    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}

    @api.multi
    def _po_line_purchase_request_cancel_message_content(self):
        self.ensure_one()
        title = _('Purchase Order %s cancelled') % self.order_id.name
        message = '<b>%s</b><br/>' % title
        message += _('The following requested item from this Purchase Request '
                     'is affected:')
        message += '<ul>'
        message += _(
            '<li><b>%s</b>: Quantity %s %s</li>'
        ) % (self.product_id.name,
             self.product_qty,
             self.product_uom.name,
             )
        message += '</ul>'
        return message

    @api.multi
    def _po_line_unlink_purchase_request_message_content(self):
        self.ensure_one()
        title = _('Line %s of Purchase Order %s was removed') % (
            self.name, self.order_id.name)
        message = '<b>%s</b><br/>' % title
        return message

    @api.multi
    def unlink(self):
        for line in self:
            message = \
                line._po_line_unlink_purchase_request_message_content()
            requests = line.purchase_request_lines.mapped('request_id')
            for req in requests:
                req.message_post(body=message, subtype='mail.mt_comment')

        return super(PurchaseOrderLine, self).unlink()
