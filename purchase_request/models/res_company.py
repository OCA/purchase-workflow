# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResConfigSettings(models.Model):
    _inherit = "res.company"

    notify_request_allocations = fields.Boolean(
        string="Send emails on confirmaion",
        default=True,
    )
