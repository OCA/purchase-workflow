# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    accrual_use_accounting_date = fields.Boolean(
        related="company_id.accrual_use_accounting_date",
        readonly=False,
    )
