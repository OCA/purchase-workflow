# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        proc_data = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id)

        if line.stock_owner_id and line.stock_owner_id != order.partner_id:
            routes = (
                line.route_id |
                self.env.ref('stock.route_warehouse0_mto') |
                self.env.ref(
                    'vendor_consignment_stock.route_warehouse0_buy_vci')
            )
            proc_data['route_ids'] = [(6, 0, routes.ids)]

        return proc_data
