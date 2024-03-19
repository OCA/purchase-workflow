# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):

    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        res = list(super()._get_procurements_to_merge_groupby(procurement))
        res.append(procurement.values["supplier"].packaging_id)
        return tuple(res)
