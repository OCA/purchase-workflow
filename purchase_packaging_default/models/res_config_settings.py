# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_packaging_default_enabled = fields.Boolean(
        related="company_id.purchase_packaging_default_enabled",
        readonly=False,
    )
