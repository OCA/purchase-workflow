# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        # Fix to prevent create record without lines
        if vals.get("stock_valuation_layer_ids") and not vals.get("line_ids"):
            return self
        return super().create(vals)
