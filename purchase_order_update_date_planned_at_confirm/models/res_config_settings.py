# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_update_date_planned_at_confirm = fields.Boolean(
        related="company_id.purchase_update_date_planned_at_confirm",
        readonly=False,
    )
