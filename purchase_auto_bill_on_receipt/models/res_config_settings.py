# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_bill_on_receipt = fields.Boolean(
        related="company_id.auto_bill_on_receipt",
        readonly=False,
    )
