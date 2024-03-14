# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _update_picking_from_group_key(self, key):
        """The picking is updated with data from the grouping key.
        This method is designed for extensibility, so that other modules
        can store more data based on new keys."""
        for rec in self:
            for key_element in key:
                if "date_planned" in key_element.keys():
                    rec.date = key_element["date_planned"]
        return False
