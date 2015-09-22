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


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_request_picking_confirm_message_content(self, picking,
                                                          request,
                                                          request_dict):
        if not request_dict:
            request_dict = {}
        title = _('Receipt confirmation %s for your Request %s') % (
            picking.name, request.name)
        message = '<h3>%s</h3>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now been received in Incoming Shipment %s:') % (
            request.name, picking.name)
        message += '<ul>'
        for line in request_dict.values():
            message += _(
                '<li><b>%s</b>: Received quantity %s %s</li>'
            ) % (line['name'],
                 line['product_qty'],
                 line['product_uom'],
                 )
        message += '</ul>'
        return message

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        request_obj = self.pool['purchase.request']
        for picking in self:
            requests_dict = {}
            if picking.picking_type_id.code != 'incoming':
                continue
            for move in picking.move_lines:
                if move.purchase_line_id:
                    for request_line in \
                            move.purchase_line_id.purchase_request_lines:
                        request_id = request_line.request_id.id
                        if request_id not in requests_dict:
                            requests_dict[request_id] = {}
                        data = {
                            'name': request_line.name,
                            'product_qty': move.product_qty,
                            'product_uom': move.product_uom.name,
                        }
                        requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict.keys():
                request = request_obj.browse(request_id)
                message = \
                    self._purchase_request_picking_confirm_message_content(
                        picking, request, requests_dict[request_id])
                request.message_post(body=message)
        return res
