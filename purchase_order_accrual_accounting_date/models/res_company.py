# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    accrual_use_accounting_date = fields.Boolean(
        string="Accrued Expenses by Accounting Date",
        help="When creating accrued expense entries, count as billed only the "
        "vendor bills with an accounting date up to the accrual date.",
    )
