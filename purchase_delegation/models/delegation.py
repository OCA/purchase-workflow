# Copyright 2022 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Delegation(models.Model):
    _inherit = "delegation"

    @api.model
    def _get_delegation_model_names(self):
        res = super()._get_delegation_model_names()
        res.append("purchase.order")
        return res
