# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super()._prepare_merge_moves_distinct_fields()
        res.append('group_id')
        return res
