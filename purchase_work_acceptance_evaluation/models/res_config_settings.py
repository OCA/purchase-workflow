# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_enable_eval_on_wa = fields.Boolean(
        string="Enable Evaluation on Work Acceptance",
        implied_group="purchase_work_acceptance_evaluation.group_enable_eval_on_wa",
    )

    @api.onchange("group_enable_eval_on_wa")
    def _onchange_group_enable_eval_on_wa(self):
        if self.group_enable_eval_on_wa:
            self.group_enable_wa_on_po = True
