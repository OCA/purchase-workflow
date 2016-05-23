# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp import api, fields, models, _, exceptions


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _purchase_request_confirm_message_content(self, po, request,
                                                  request_dict):
        if not request_dict:
            request_dict = {}
        title = _('Order confirmation %s for your Request %s') % (
            po.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now been confirmed in Purchase Order %s:') % (
            request.name, po.name)

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
                for request_line in line.purchase_request_lines:
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
            for request_id in requests_dict.keys():
                request = request_obj.browse(request_id)
                message = self._purchase_request_confirm_message_content(
                    po, request, requests_dict[request_id])
                request.message_post(body=message, subtype='mail.mt_comment')
        return True

    @api.multi
    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.purchase_state == 'done':
                        raise exceptions.Warning(
                            _('Purchase Request %s has already '
                              'been completed') % request_line.request_id.name)
        return True

    @api.multi
    def wkf_confirm_order(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).wkf_confirm_order()
        self._purchase_request_confirm_message()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.one
    def _has_purchase_request_lines(self):
        if self.purchase_request_lines:
            self.has_purchase_request_lines = True
        else:
            self.has_purchase_request_lines = False

    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_order_line_id',
        'purchase_request_line_id',
        'Purchase Request Lines', readonly=True)
    has_purchase_request_lines = fields.Boolean(
        compute="_has_purchase_request_lines",
        string="Has Purchase Request Lines")

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'purchase_request_lines': [],
        })
        return super(PurchaseOrderLine, self).copy(default)

    @api.multi
    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids = [request_line.id for request_line
                                in line.purchase_request_lines]
        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}
