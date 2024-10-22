# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        return (
            procurement.values.get("restrict_lot_id"),
            super()._get_procurements_to_merge_groupby(procurement),
        )
