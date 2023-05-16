# Copyright 2021 - 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("secondary_uom_id")
        return distinct_fields

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res["secondary_uom_id"] = self.secondary_uom_id.id
        res["secondary_uom_qty"] = self.secondary_uom_qty
        return res
