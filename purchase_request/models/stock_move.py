# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_request_allocation_ids = fields.One2many(
        comodel_name='purchase.request.allocation',
        inverse_name='stock_move_id',
        string='Purchase Request Allocation')

    @api.model
    def _stock_request_confirm_done_message_content(self, message_data):
        title = _('Receipt confirmation %s for your Request %s') % (
            message_data['picking_name'], message_data['request_name'])
        message = '<h3>%s</h3>' % title
        message += _('The following requested items from Stock Request %s '
                     'have now been received in %s using Picking %s:') % (
            message_data['request_name'], message_data['location_name'],
            message_data['picking_name'])
        message += '<ul>'
        message += _(
            '<li><b>%s</b>: Transferred quantity %s %s</li>'
        ) % (message_data['product_name'],
             message_data['product_qty'],
             message_data['product_uom'],
             )
        message += '</ul>'
        return message

    def _prepare_message_data(self, ml, request, allocated_qty):
        return {
            'request_name': request.name,
            'picking_name': ml.picking_id.name,
            'product_name': ml.product_id.name_get()[0][1],
            'product_qty': allocated_qty,
            'product_uom': ml.product_uom.name,
            'location_name': ml.location_dest_id.name_get()[0][1],
        }

    @api.multi
    def allocate_refresh(self):
        for ml in self.filtered(
                lambda m: m.exists() and m.purchase_request_allocation_ids):
            qty_done = ml.product_uom._compute_quantity(
                ml.product_qty, ml.product_id.uom_id)

            # We do sudo because potentially the user that completes the move
            #  may not have permissions for stock.request.
            to_allocate_qty = qty_done
            for allocation in ml.purchase_request_allocation_ids.sudo():
                allocated_qty = 0.0
                if allocation.open_product_qty:
                    allocated_qty = min(
                        allocation.open_product_qty, qty_done)
                    allocation.allocated_product_qty += allocated_qty
                    to_allocate_qty -= allocated_qty
                if allocated_qty:
                    request = allocation.purchase_request_line_id.request_id
                    message_data = self._prepare_message_data(ml, request,
                                                              allocated_qty)
                    message = \
                        self._stock_request_confirm_done_message_content(
                            message_data)
                    request.message_post(
                        body=message, subtype='mail.mt_comment')
                    request.check_done()

        return self

    @api.multi
    def action_done(self):
        self.allocate_refresh()
        res = super(StockMove, self).action_done()
        return res

    @api.model
    def copy_data(self, default=None):
        if not default:
            default = {}
        if 'purchase_request_allocation_ids' not in default:
            default['purchase_request_allocation_ids'] = []
        for alloc in self.purchase_request_allocation_ids:
            default['purchase_request_allocation_ids'].append((0, 0, {
                'purchase_request_line_id': alloc.purchase_request_line_id.id,
                'requested_product_uom_qty':
                    alloc.requested_product_uom_qty,
            }))
        return super(StockMove, self).copy_data(default)

    def action_cancel(self):
        res = super(StockMove, self).action_cancel()
        self.mapped(
            'purchase_request_allocation_ids.'
            'purchase_request_line_id').check_done()
        return res
