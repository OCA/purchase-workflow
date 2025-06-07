# © 2016 ForgeFlow S.L.
#   (<http://www.forgeflow.com>)
# © 2018 Hizbul Bahar <hizbul25@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination",
        domain=[("usage", "in", ["internal", "transit"])],
    )

    def _purchase_split_date_get_group_keys(self, picking):
        key = super()._purchase_split_date_get_group_keys(picking)
        default_picking_location_id = self.order_id._get_destination_location()
        default_picking_location = self.env["stock.location"].browse(
            default_picking_location_id
        )
        location = self.location_dest_id or default_picking_location
        return key + ({"location_dest_id": location.id},)

    def _purchase_split_date_get_sorted_keys(self):
        keys = super()._purchase_split_date_get_sorted_keys()
        return keys + (self.location_dest_id.id,)

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        if self.location_dest_id:
            for re in res:
                re["location_dest_id"] = self.location_dest_id.id
        return res
