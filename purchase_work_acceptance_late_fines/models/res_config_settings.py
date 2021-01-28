# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_enable_fines_on_wa = fields.Boolean(
        string="Enable Late Delivery Fines on Work Acceptance",
        implied_group="purchase_work_acceptance_late_fines.group_enable_fines_on_wa",
    )
    wa_fines_late_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.wa_fines_late_account_id",
        string="Late Delivery Fines Revenue Account",
        readonly=False,
    )
    wa_fines_rate = fields.Monetary(
        related="company_id.wa_fines_rate",
        string="Fines Rate",
        readonly=False,
    )

    @api.onchange("group_enable_fines_on_wa")
    def _onchange_group_enable_fines_on_wa(self):
        if self.group_enable_fines_on_wa:
            self.group_enable_wa_on_po = True
