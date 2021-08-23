# Copyright 2016 ForgeFlow S.L. (<http://www.forgeflow.com>)
# Copyright 2018 Hizbul Bahar <hizbul25@gmail.com>
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination",
        domain=[("usage", "in", ["internal", "transit"])],
    )

    def _is_valid_picking(self, picking):
        res = super()._is_valid_picking(picking)
        if not res:
            return res
        location = self.location_dest_id or self.env["stock.location"].browse(
            self.order_id._get_destination_location()
        )
        return picking.location_dest_id == location

    def _prepare_stock_moves(self, picking):
        # When the first move of the picking is prepared, ensure the
        # destination of the picking to make it a valid candidate
        if not picking.move_lines:
            location = self.location_dest_id or self.env["stock.location"].browse(
                self.order_id._get_destination_location()
            )
            if picking.location_dest_id != location:
                picking.location_dest_id = location
        return super()._prepare_stock_moves(picking)
