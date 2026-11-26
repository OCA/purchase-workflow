# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_bill_on_receipt = fields.Boolean(
        string="Auto Bill on Purchase Receipt",
        help="When enabled, validating an incoming purchase receipt "
        "automatically creates and posts a Vendor Bill. This is the default "
        "for all vendors and can be overridden per vendor.",
    )
