# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class WorkAcceptance(models.Model):
    _name = "work.acceptance"
    _inherit = ["work.acceptance", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["accept"]

    _tier_validation_manual_config = False
