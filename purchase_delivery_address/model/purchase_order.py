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

from openerp import models, api, exceptions
from openerp.tools.translate import _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('dest_address_id')
    def new_onchange_dest_address_id(self):
        """Find a picking type from the address

        If the address can be an internal warehouse or a customer, the picking
        type is changed accordingly. This intentionally overrides the original
        without super, and should be consistent with the module
        purchase_requisition_delivery_address.

        """
        PickType = self.env['stock.picking.type']
        types = PickType.search([
            ('warehouse_id.partner_id', '=', self.dest_address_id.id)])

        if types:
            if self.picking_type_id in types:
                return
            picking_type = types[0]
        elif self.dest_address_id.customer:
            # if destination is not for a warehouse address,
            # we set dropshipping picking type
            ref = 'stock_dropshipping.picking_type_dropship'
            picking_type = self.env.ref(ref)
        else:
            raise exceptions.Warning(_(
                'No picking types were found on warehouse. Please verify you '
                'have set an address on warehouse.'))
        self.picking_type_id = picking_type

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        """If the picking type has an address, use it.

        We cannot empty the address if one is not found, because that gives a
        short circuit with the onchange of the address.

        """

        if self.picking_type_id:
            pick_type = self.picking_type_id

            if pick_type.warehouse_id.partner_id:
                self.dest_address_id = pick_type.warehouse_id.partner_id.id

            if pick_type.default_location_dest_id:
                self.location_id = pick_type.default_location_dest_id
                self.related_location_id = pick_type.default_location_dest_id

    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        for order in self:
            order.picking_ids.write({
                'partner_id': order.partner_id.id,
                'delivery_address_id': order.dest_address_id.id
            })
        return res
