# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    auto_bill_on_receipt = fields.Selection(
        selection=[
            ("auto", "Auto Bill"),
            ("no_auto", "No Auto Bill"),
        ],
        string="Auto Bill on Purchase Receipt",
        help="Override the company default for auto-billing on purchase "
        "receipt. Leave empty to inherit the company setting.",
    )
