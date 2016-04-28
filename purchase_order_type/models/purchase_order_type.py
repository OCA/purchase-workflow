# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

from openerp import models, fields, api


class PurchaseOrderType(models.Model):
    _name = 'purchase.order.type'

    @api.model
    def _get_selection_invoice_method(self):
        return self.env['purchase.order'].fields_get(
            allfields=['invoice_method'])['invoice_method']['selection']

    def default_invoice_method(self):
        default_dict = self.env[
            'purchase.order'].default_get(['invoice_method'])
        return default_dict.get('invoice_method')

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    invoice_method = fields.Selection(
        selection='_get_selection_invoice_method', string='Create Invoice',
        required=True, default=default_invoice_method)
