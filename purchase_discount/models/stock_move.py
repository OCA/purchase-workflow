# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        if self.env.context.get("skip_update_price_unit") and values.get("price_unit"):
            values.pop("price_unit")
        return super().write(values)
