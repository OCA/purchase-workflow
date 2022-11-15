# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    number_of_day_lock_po = fields.Integer(
        related="company_id.number_of_day_lock_po", readonly=False
    )
