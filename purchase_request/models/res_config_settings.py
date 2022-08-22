# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    notify_request_allocations = fields.Boolean(
        related="company_id.notify_request_allocations",
        string="Send emails with request confirmaion",
        readonly=False,
    )
