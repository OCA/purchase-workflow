# © 2016 ForgeFlow S.L.
#   (<http://www.forgeflow.com>)
# © 2018 Hizbul Bahar <hizbul25@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination",
        domain=[("usage", "in", ["internal", "transit"])],
    )

    @api.model
    def _first_picking_copy_vals(self, key, lines):
        """The data to be copied to new pickings is updated with data from the
        grouping key.  This method is designed for extensibility, so that
        other modules can store more data based on new keys."""
        vals = super()._first_picking_copy_vals(key, lines)
        for key_element in key:
            if "location_dest_id" in key_element.keys():
                vals["location_dest_id"] = key_element["location_dest_id"].id
        return vals

    @api.model
    def _get_group_keys(self, order, line, picking=False):
        """Define the key that will be used to group. The key should be
        defined as a tuple of dictionaries, with each element containing a
        dictionary element with the field that you want to group by. This
        method is designed for extensibility, so that other modules can add
        additional keys or replace them by others."""
        key = super()._get_group_keys(order, line, picking=picking)
        default_picking_location_id = line.order_id._get_destination_location()
        default_picking_location = self.env["stock.location"].browse(
            default_picking_location_id
        )
        location = line.location_dest_id or default_picking_location
        return key + ({"location_dest_id": location},)

    def _get_sorted_keys(self, line):
        """Return a tuple of keys to use in order to sort the order lines.
        This method is designed for extensibility, so that other modules can
        add additional keys or replace them by others."""
        keys = super()._get_sorted_keys(line)
        return keys + (line.location_dest_id.id,)

    def _create_stock_moves(self, picking):
        res = super()._create_stock_moves(picking)
        updated_pickings = self.env["stock.picking"]
        for line in self:
            default_picking_location_id = line.order_id._get_destination_location()
            default_picking_location = self.env["stock.location"].browse(
                default_picking_location_id
            )
            location = line.location_dest_id or default_picking_location
            if location:
                moves = line.move_ids.filtered(
                    lambda m: m.state != "done" and (not picking or m.picking_id == picking)
                )
                if moves:
                    moves.write({"location_dest_id": location.id})
                    updated_pickings |= moves.picking_id
        for picking_rec in updated_pickings:
            move_locations = picking_rec.move_ids.filtered(
                lambda m: m.state != "cancel"
            ).mapped("location_dest_id")
            if len(move_locations) == 1 and move_locations != picking_rec.location_dest_id:
                picking_rec.location_dest_id = move_locations.id
        return res
