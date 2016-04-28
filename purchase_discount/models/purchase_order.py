# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _calc_line_base_price(self, line):
        res = super(PurchaseOrderLine, self)._calc_line_base_price(line)
        return res * (1 - line.discount / 100.0)

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        result = super(PurchaseOrder, self)._prepare_inv_line(
            account_id, order_line)
        result['discount'] = order_line.discount or 0.0
        return result

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id,
                                 group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        for vals in res:
            vals['price_unit'] = (vals.get('price_unit', 0.0) *
                                  (1 - (order_line.discount / 100)))
        return res
