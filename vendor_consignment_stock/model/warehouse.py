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
from openerp import models, api, fields, exceptions
from openerp.tools.translate import _


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    buy_vci_to_resupply = fields.Boolean(
        'Purchase from VCI to resupply this warehouse',
        help="This warehouse can contain Vendor-Supplied-Inventory (VCI) that "
             "have to be bought before being sold.",
        default=True)
    buy_vci_pull_id = fields.Many2one('procurement.rule', 'BUY VCI rule')

    @api.model
    def _get_buy_vci_pull_rule(self, warehouse):
        route_model = self.env['stock.location.route']
        try:
            buy_vci_route = self.env.ref(
                'vendor_consignment_stock.route_warehouse0_buy_vci')
        except:
            buy_vci_route = route_model.search([
                ('name', 'like', _('Buy VCI'))
            ])
        if not buy_vci_route:
            raise exceptions.Warning(_(
                'Can\'t find any generic Buy VCI route.'))

        return {
            'name': self._format_routename(warehouse, _('Buy VCI')),
            'location_id': warehouse.int_type_id.default_location_dest_id.id,
            'route_id': buy_vci_route.id,
            'action': 'buy_vci',
            'picking_type_id': warehouse.int_type_id.id,
            'warehouse_id': warehouse.id,
        }

    @api.multi
    def create_routes(self, warehouse):
        pull_model = self.env['procurement.rule']
        res = super(Warehouse, self).create_routes(warehouse)
        if warehouse.buy_vci_to_resupply:
            buy_vci_pull_vals = self._get_buy_vci_pull_rule(warehouse)
            buy_vci_pull = pull_model.create(buy_vci_pull_vals)
            res['buy_vci_pull_id'] = buy_vci_pull.id
        return res

    @api.multi
    def write(self, vals):
        pull_model = self.env['procurement.rule']

        if 'buy_vci_to_resupply' in vals:
            if vals.get("buy_vci_to_resupply"):
                for warehouse in self:
                    if not warehouse.buy_vci_pull_id:
                        buy_vci_pull_vals = self._get_buy_vci_pull_rule(
                            warehouse)
                        buy_vci_pull = pull_model.create(buy_vci_pull_vals)
                        vals['buy_vci_pull_id'] = buy_vci_pull.id
            else:
                for warehouse in self:
                    if warehouse.buy_vci_pull_id:
                        warehouse.buy_vci_pull_id.unlink()
        return super(Warehouse, self).write(vals)

    @api.model
    def get_all_routes_for_wh(self, warehouse):
        all_routes = super(Warehouse, self).get_all_routes_for_wh(warehouse)
        if (
            warehouse.buy_vci_to_resupply and
            warehouse.buy_vci_pull_id.route_id
        ):
            all_routes += [warehouse.buy_vci_pull_id.route_id.id]
        return all_routes

    @api.model
    def _get_all_products_to_resupply(self, warehouse):
        product_ids = super(Warehouse, self)._get_all_products_to_resupply(
            warehouse)
        if warehouse.buy_vci_pull_id.route_id:
            for product in self.env['product.product'].browse(product_ids):
                for route in product.route_ids:
                    if route == warehouse.buy_vci_pull_id.route_id:
                        product_ids.remove(product.id)
                        break
        return product_ids

    @api.model
    def _handle_renaming(self, warehouse, name, code):
        res = super(Warehouse, self)._handle_renaming(warehouse, name, code)

        # change the buy vci pull rule name
        if warehouse.buy_vci_pull_id:
            warehouse.buy_vci_pull_id.name = (
                warehouse.buy_vci_pull_id.name.replace(warehouse.name, name, 1)
            )
        return res

    @api.multi
    def change_route(self, warehouse, new_reception_step=False,
                     new_delivery_step=False):
        res = super(Warehouse, self).change_route(
            warehouse,
            new_reception_step=new_reception_step,
            new_delivery_step=new_delivery_step)
        if (warehouse.int_type_id.default_location_dest_id !=
                warehouse.buy_vci_pull_id.location_id):
            warehouse.buy_vci_pull_id.location_id = (
                warehouse.int_type_id.default_location_dest_id)
        return res
