# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, exceptions, fields, models


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
                        raise exceptions.UserError(
                            _('Purchase Request %s has already '
                              'been completed') % request_line.request_id.name)
        return True

    @api.multi
    def button_confirm(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).button_confirm()
        self._purchase_request_confirm_message()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_order_line_id',
        'purchase_request_line_id',
        'Purchase Request Lines', readonly=True, copy=False)

    purchase_request_allocation_ids = fields.One2many(
        comodel_name='purchase.request.allocation',
        inverse_name='purchase_line_id',
        string='Purchase Request Allocation')

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
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        all_list = []
        for v in val:
            all_ids = self.env['purchase.request.allocation'].search(
                [('purchase_line_id', '=', v['purchase_line_id'])]
            )
            for all_id in all_ids:
                all_list.append((4, all_id.id))
            v['purchase_request_allocation_ids'] = all_list
        return val

    @api.multi
    def update_service_allocations(self, prev_qty_received):
        for rec in self:
            allocation = self.env['purchase.request.allocation'].search(
                [('purchase_line_id', '=', rec.id),
                 ('purchase_line_id.product_id.type', '=', 'service')]
            )
            if not allocation:
                return
            qty_left = rec.qty_received - prev_qty_received
            for alloc in allocation:
                allocated_product_qty = alloc.allocated_product_qty
                if not qty_left:
                    alloc.purchase_request_line_id._compute_qty()
                    break
                if alloc.open_product_qty <= qty_left:
                    allocated_product_qty += alloc.open_product_qty
                    qty_left -= alloc.open_product_qty
                    alloc._notify_allocation(alloc.open_product_qty)
                else:
                    allocated_product_qty += qty_left
                    alloc._notify_allocation(qty_left)
                    qty_left = 0
                alloc.write({'allocated_product_qty': allocated_product_qty})

                message_data = self._prepare_request_message_data(
                    alloc,
                    alloc.purchase_request_line_id,
                    allocated_product_qty)
                message = \
                    self._purchase_request_confirm_done_message_content(
                        message_data)
                alloc.purchase_request_line_id.request_id.message_post(
                    body=message, subtype='mail.mt_comment')

                alloc.purchase_request_line_id._compute_qty()
        return True

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _('Service confirmation for Request %s') % (
            message_data['request_name'])
        message = '<h3>%s</h3>' % title
        message += _('The following requested services from Purchase'
                     ' Request %s requested by %s '
                     'have now been received:') % (
            message_data['request_name'], message_data['requestor'])
        message += '<ul>'
        message += _(
            '<li><b>%s</b>: Received quantity %s %s</li>'
        ) % (message_data['product_name'],
             message_data['product_qty'],
             message_data['product_uom'],
             )
        message += '</ul>'
        return message

    def _prepare_request_message_data(
            self, alloc, request_line, allocated_qty):
        return {
            'request_name': request_line.request_id.name,
            'product_name': request_line.product_id.name_get()[0][1],
            'product_qty': allocated_qty,
            'product_uom': alloc.product_uom_id.name,
            'requestor': request_line.request_id.requested_by.partner_id.name,
        }

    @api.multi
    def write(self, vals):
        #  it is done here instead of method _update_received_qty
        #  to make sure this work for services
        prev_qty_received = self.qty_received
        res = super(PurchaseOrderLine, self).write(vals)
        if vals.get('qty_received', False):
            self.update_service_allocations(prev_qty_received)
        return res
