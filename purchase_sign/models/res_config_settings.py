# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_portal_confirmation_sign = fields.Boolean(
        related="company_id.purchase_portal_confirmation_sign",
        readonly=False,
    )
