# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_purchase_return(self):
        if super()._is_purchase_return():
            return True
        physical_move = self.origin_returned_move_id
        if not (
            self.location_dest_id.usage == "transit"
            and physical_move.location_id.usage == "transit"
            and physical_move.location_dest_id.usage == "internal"
        ):
            return False
        transit_locations = self.env[
            "stock.warehouse"
        ]._get_incoming_transit_locations()
        return (
            self.location_dest_id in transit_locations
            and physical_move.location_id in transit_locations
        )
