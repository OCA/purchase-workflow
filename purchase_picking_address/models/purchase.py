# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        picking = self.picking_type_id
        if picking.default_location_dest_id.usage == 'internal':
            self.dest_address_id = picking.purchase_delivery_address_id
            return
        super()._onchange_picking_type_id()

    def _get_destination_location(self):
        self.ensure_one()
        picking_type = self.picking_type_id
        if (
            self.dest_address_id and
            picking_type.purchase_delivery_address_id == self.dest_address_id
        ):
            return picking_type.default_location_dest_id.id
        return super()._get_destination_location()
