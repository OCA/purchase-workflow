# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        groupby = super()._get_procurements_to_merge_groupby(procurement)
        res = *groupby, procurement.values.get("date_planned").date()
        return res
