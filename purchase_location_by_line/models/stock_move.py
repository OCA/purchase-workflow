# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _purchase_split_date_get_group_keys(self):
        key = super()._purchase_split_date_get_group_keys()
        return key + ({"location_dest_id": self.location_dest_id.id},)
