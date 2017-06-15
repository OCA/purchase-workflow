# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        proc_data = super(SaleOrder, self)._prepare_order_line_procurement(
            group_id)

        if (
            self.stock_owner_id and
            self.stock_owner_id != self.order_id.partner_id
        ):
            routes = (
                self.route_id |
                self.env.ref('stock.route_warehouse0_mto') |
                self.env.ref(
                    'vendor_consignment_stock.route_warehouse0_buy_vci')
            )
            proc_data['route_ids'] = [(6, 0, routes.ids)]

        return proc_data
