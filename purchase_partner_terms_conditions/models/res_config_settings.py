# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_partner_purchase_conditions_commercial = fields.Boolean(
        related="company_id.is_partner_purchase_conditions_commercial", readonly=False
    )
