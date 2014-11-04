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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def onchange_dest_address_id(self, dest_address_id):
        """If we enter a delivery address, normally it is a dropshipping-like
        situation, so we choose an appropriate picking type.

        """
        res = super(PurchaseOrder, self).onchange_dest_address_id(
            dest_address_id)
        if dest_address_id:
            new_picktype = self.env['stock.picking.type'].search([
                ('default_location_src_id.usage', '=', 'supplier'),
                ('default_location_dest_id.usage', '=', 'customer'),
            ], limit=1)

            if new_picktype:
                res['value']['picking_type_id'] = new_picktype.id

        return res

    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        for order in self:
            order.picking_ids.write({
                'partner_id': order.partner_id.id,
                'delivery_address_id': order.dest_address_id.id
            })
        return res
