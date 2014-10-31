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

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_address_id = fields.Many2one('res.partner', 'Delivery Address')

    @api.onchange('delivery_address_id')
    def _onchange_delivery_address(self):
        """If we enter a delivery address, normally it is a dropshipping-like
        situation, so we choose an appropriate picking type.

        """
        if self.delivery_address_id:
            new_picktype = self.env['stock.picking.type'].search([
                ('default_location_src_id.usage', '=', 'supplier'),
                ('default_location_dest_id.usage', '=', 'customer'),
            ], limit=1)

            if new_picktype:
                self.picking_type_id = new_picktype

    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        for order in self:
            order.picking_ids.write(
                {'delivery_address_id': order.delivery_address_id.id})
        return res
