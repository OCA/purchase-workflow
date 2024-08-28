# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_transport_mode_contraint_enabled = fields.Boolean(
        related="company_id.purchase_transport_mode_contraint_enabled",
        readonly=False,
        string="Validate purchase transport mode",
    )
