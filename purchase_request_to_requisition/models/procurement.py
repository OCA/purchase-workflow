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
from openerp import api, fields, models, _


class Procurement(models.Model):
    _inherit = 'procurement.order'

    request_id = fields.Many2one('purchase.request',
                                 string='Latest Purchase Request')

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['request_id'] = False
        return super(Procurement, self).copy(default)

    @api.model
    def _prepare_purchase_request_line(self, procurement):
        return {
            'product_id': procurement.product_id.id,
            'name': procurement.product_id.name,
            'date_required': procurement.date_planned,
            'product_uom_id': procurement.product_uom.id,
            'product_qty': procurement.product_qty
        }

    @api.model
    def _prepare_purchase_request(self, procurement):
        warehouse_obj = self.env['stock.warehouse']
        request_line_data = self._prepare_purchase_request_line(procurement)
        warehouse_id = warehouse_obj.search([('company_id', '=',
                                              procurement.company_id.id)])
        return {
            'origin': procurement.origin,
            'company_id': procurement.company_id.id,
            'warehouse_id': warehouse_id,
            'line_ids': [(4, request_line_data)]
        }

    @api.model
    def _run(self, procurement):
        request_obj = self.env['purchase.request']
        if procurement.rule_id and procurement.rule_id.action == 'buy' \
                and procurement.product_id.purchase_request:
            request_data = self._prepare_purchase_request(procurement)
            req = request_obj.create(request_data)
            procurement.message_post(body=_("Purchase Request created"))
            procurement.request_id = req.id
            return True
        return super(Procurement, self)._run(procurement)
